#===================================================#
#                     Imports                       #
#===================================================#
import os
import sys
import threading
import subprocess
import socket
import json
from datetime import datetime
from datetime import timedelta
import hashlib
from Crypto.Cipher import AES
import base64
import time

#===================================================#
#                   Global config                   #
#===================================================#
# AS config
myASN = sys.argv[1]
myAddress = sys.argv[2]
myIP = sys.argv[2].split(":")[0]
myPort = sys.argv[2].split(":")[1]
myService = sys.argv[3]
myPrivKey = ""
myPubKey = ""
myUser = sys.argv[5]
ordererIP = 'grpc://'+sys.argv[6]+':7050'

# Dictionaries contanining the offers that the AS have sent and received
offersSent = {}
offersRecvd = {}

# Dictionary containing the AS' interconnetion agreements
agreementsCust = {}
agreementsProv = {}

# Evaluation log
logs = open(myASN+".log", "w")

#===================================================#
#                     Functions                     #
#===================================================#

# Command line interface. Reads an instructions and call the appropriate function.
def cli():

    while True:
        action = raw_input("Dynam-IX: ")
        if len(action) > 0:
            if "registerAS" in action: # registerAS 'ASN' 'address' 'service' 'custRep' 'provRep' 'pubKey'
                x = subprocess.check_output('node register.js '+action+' '+myUser+' '+ordererIP, shell=True)
                print x
            elif "listASes" in action:  # listASes 
                x = subprocess.check_output('node list.js'+' '+myUser, shell=True)
                print x
            elif "findService" in action: # findService service         # TODO fix this function when string has space
                #queryString = "{\"selector\":{\"service\":\"Transit\"}}"
                service = action.split("- ")[1]
                print service
                x = subprocess.check_output('node query.js findService \'{\"selector\":{\"service\":\"'+service+'\"}}\''+' '+myUser, shell=True)
                print x
            elif "show" in action: #show 'key'
                x = subprocess.check_output('node query.js '+action+' '+myUser, shell=True)
                print x
            elif "history" in action: #history 'key'
                x = subprocess.check_output('node query.js '+action+' '+myUser, shell=True)
                print x
            elif "delete" in action: #delete 'key'
                x = subprocess.check_output('node delete.js '+action+' '+myUser+' '+ordererIP, shell=True)
                print x
            elif "updateService" in action: #updateService 'ASN' 'newService'
                x = subprocess.check_output('node update.js '+action+' '+myUser+' '+ordererIP, shell=True)
                print x
            elif "updateAddress" in action: #updateAddress 'ASN' 'newAddress'
                x = subprocess.check_output('node update.js '+action+' '+myUser+' '+ordererIP, shell=True)
                print x
            elif "query" in action: #query providerASN request
                sendQuery(action)
            elif "propose" in action: #propose ID
                sendProposal(action)
            elif "listAgreements" in action:
                x = subprocess.check_output('node listAgreements.js'+' '+myUser, shell=True)
                print x
            elif "listOffersSent" in action:
                listOffersSent()
            elif "listOffersRecvd" in action:
                listOffersRecvd()
            elif "myAgreements" in action:
                myAgreements()
            elif "executeAgreements" in action:
                executeAgreements()
            elif "autonomous" in action:
                autonomous()
            elif "updateIntents" in action:
                intents = json.load(open(action.split(" ")[1]))
            elif "quit" in action:
                print "Quiting Dynam-IX"
                logs.close()
                os._exit(1)
            else:
                print "Invalid command\n"

    return


def autonomous():

    print "Entering autonomous mode!"

    AS = "AS1"
    num = int(sys.argv[8])
    sleepTime = int(sys.argv[9])

    print "Going to interact with "+AS+" doing "+str(num)+" queries/proposals every "+str(sleepTime)+" seconds"

    global offersRecvd

    total = 0
    while total < 100:
        offersRecvd = {}

        for i in range(0,num):
            #query AS prefix
            query = "query "+AS+" 8.8.8.0/24"
            sendQuery(query)

        while len(offersRecvd) < num:
            print "Number of offers: "+str(len(offersRecvd))
            time.sleep(1)

        for offer in offersRecvd.keys():
            offerID = offer

            proposal = "propose "+offerID
            #propose offerID
            sendProposal(proposal)

        total = total + num
        print "Sleeping"
        time.sleep(sleepTime)
        print "Waking up"

    print "Leaving autonomous mode!"
    time.sleep(30)  # Be sure of getting all agreements
    print "Quiting Dynam-IX"
    logs.close()
    os._exit(1)

# Receive messages and create threads to process them
def processMessages():

    messageThreads = []

    # Open socket to accept connections
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    serversocket.bind((myIP, int(myPort)))
    serversocket.listen(256) # NOTE We may need to increase the number simultaneous requests 

    while True:
        connection, address = serversocket.accept()
        msg = ''
        msg = connection.recv(1024)     # NOTE We may need to change the amount of received bytes
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        if len(msg) > 0:
            if "query" in msg:  # Customer is asking for an offer
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RQ;"+msg.split(";")[3]+"\n")
                t = threading.Thread(target=sendOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "offer" in msg: # Provider have sent an offer
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RO;"+msg.split(";")[3]+"\n")
                t = threading.Thread(target=collectOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "propose" in msg: # Customer is asking to establish an interconnection agreement
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RP;"+msg.split(";")[1]+"\n")
                t = threading.Thread(target=establishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "contract" in msg: # Provider have sent the contract to be signed
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RC;"+msg.split(";")[1]+"\n")
                t = threading.Thread(target=signContract, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "publish" in msg:  # Customer is sending the signed contract to be registered on the ledger
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RS;"+msg.split(";")[1]+"\n")
                t = threading.Thread(target=publishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "ack" in msg:  # Customer is sending the signed contract to be registered on the ledger
                print "Success! Updating routing configuration!"
                # logging
#                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                logs.write(timestamp+";RU;"+msg.split(";")[1]+"\n")
            else:
                print "Invalid message\n"

def sendMessage(msg, ip, port):

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ip, port))
    clientsocket.send(msg)
    clientsocket.close()

# Receives a query action and send it to a potential provider
def sendQuery(action):

    # Get provider's ASN
    provider = action.split(" ")[1]
    # Query the ledger to get the provider's address
    address = ""
    while ":" not in address:
        address = getAddress(provider)
    # Split the address into IP and port
    IP = address.split(":")[0]
    port = int(address.split(":")[1])
    # Get the query
    query = action.split(" ")[2]
    # Query the ledger to get the provider's public key
    pubkey = getPubKey(provider)

    # Evaluation control
    # Generate the query/offer ID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    ID = myASN+"-"+provider+"-"+timestamp

    # Create the message that is going to be sent
    msg = 'query;'+myASN+';'+query+";"+ID # TODO encrypt with provider's pubkey

    # logging
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    # Send the query to the provider   
    sendMessage(msg, IP, port)

    # logging
    logs.write(timestamp+";SQ;"+ID+"\n")


# get AS' reputation as a customer or as a provider from the ledger
def getReputation(ASN, role):

    x=""

    while "address" not in x:
        # Query the ledger to get AS' information
        x = subprocess.check_output('node query.js show \''+ASN+'\''+' '+myUser, shell=True)
    # Get the reputation
    if role == "customer":
        return x.split(",")[1].split(':')[1]
    elif role == "provider":
        return x.split(",")[2].split(':')[1]

# get AS' address from the ledger
def getAddress(ASN):

    x=""

    while "address" not in x:
        # Query the ledger to get AS' information
        x = subprocess.check_output('node query.js show \''+ASN+'\''+' '+myUser, shell=True)
    # Get the address
    aux = x.split(",")[0]
    ip = aux.split(":")[1]
    port = aux.split(":")[2]

    # Return ip:port
    return ip.split("\"")[1]+":"+port.split("\"")[0]

# get AS' public key from the ledger
def getPubKey(ASN):

    x=""

    while "address" not in x:
        # Query the ledger to get AS' information
        x = subprocess.check_output('node query.js show \''+ASN+'\''+' '+myUser, shell=True)
    S = x.split(",")[3].split(":")[1]

    return S.split("\"")[1]

# Receive a query from a customer, decide if it is going to answer, and compose and agreement offer 
def sendOffer(query):
    # queryFormat = query;customerASN;properties
    print "debug: Received : "+query

    # Get customer's ASN
    customer = query.split(";")[1]
    # Verify customer's reputation
    reputation = 1 #getReputation(customer, "customer")
    # If AS is a good customer, send offer
    if int(reputation) >= 0:                # TODO Define reputation threshold
        # Check interconnection policy to compose and offer to the customer
        ID = query.split(";")[3]
        offer = composeOffer(query.split(";")[2], customer, ID)
        # If provider can offer something, send
        if offer != -1:
            # Get customer's address
            address = ""
            while ":" not in address:
                address = getAddress(customer)
            print "Got address "+address+" for query "+query
            # Split address into IP and port
            IP = address.split(':')[0]
            port = int(address.split(':')[1])
            # Get customer's public key
            pubKey = getPubKey(customer)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            #Send offer
            sendMessage(offer+";"+ID, IP, port)

            # logging
            logs.write(timestamp+";SO;"+ID+"\n")

        # Provider is not able to offer an agreement with the desired properties
        else:
           print "I cannot offer an agreement!"
    # Customer has poor reputation
    else:
        print "Customer with poor reputation!"

# Check the interconnection policy and compose and offer to be sent to the customer
def composeOffer(query, customer, ID):

    # Generate the offer ID
#    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#    ID = myASN+"-"+customer+"-"+timestamp

#    offer = "offer;"+ID+";"+query+";10$;"+expireDate
    properties = checkIntents(query)

    if properties != -1:
        # Store the offer on the list. This is important to verify if the offer is still valid when the customer sends the proposal message.
        storeOffer(ID+";"+properties, "sent")
        #return offer
        return "offer;"+ID+";"+properties
    else:
        return properties


def checkIntents(query):

    customerIntent = query # TODO improve

    #print "customer intent "+customerIntent

    i = 1
    # iterate over provider's intents
    while "intent-"+str(i) in intents:
        #print i, str(intents["intent-"+str(i)]["routing"]["reachability"])
        if str(intents["intent-"+str(i)]["routing"]["reachability"]) == customerIntent:
            offer = fillOffer(i)
            return offer
        i = i + 1

    # return -1 if the provider cannot offer an agreement with the desired propertiess
    return -1

def fillOffer(i):

    reachability = "routing.reachability:"+str(intents["intent-"+str(i)]["routing"]["reachability"])
    aspath = ",routing.aspath:"+str(intents["intent-"+str(i)]["routing"]["aspath"])
    bandwidth = ",sla.bandwidth:"+str(intents["intent-"+str(i)]["sla"]["bandwidth"])
    latency = ",sla.latency:"+str(intents["intent-"+str(i)]["sla"]["latency"])
    loss = ",sla.loss:"+str(intents["intent-"+str(i)]["sla"]["loss"])
    repair = ",sla.repair:"+str(intents["intent-"+str(i)]["sla"]["repair"])
    guarantee = ",sla.guarantee:"+str(intents["intent-"+str(i)]["sla"]["guarantee"])
    egress = ",pricing.egress:"+str(intents["intent-"+str(i)]["pricing"]["egress"])
    ingress = ",pricing.ingress:"+str(intents["intent-"+str(i)]["pricing"]["ingress"])
    billing = ",pricing.billing:"+str(intents["intent-"+str(i)]["pricing"]["billing"])
    length = ",time.length:"+str(intents["intent-"+str(i)]["time"]["unit"])
    expireDate = ",time.expire:"+str(datetime.now() + timedelta(hours=6))

    offer = reachability+aspath+bandwidth+latency+loss+repair+guarantee+egress+ingress+billing+length+expireDate

    return offer


# Receive an offer and store it on the appropriate dictionary
def collectOffer(offer):
    
    ID = offer.split(";")[1]
    properties = offer.split(";")[2]

    print "Received: "+ offer
    storeOffer(ID+";"+properties, "recvd")

# Store an offer on the appropriate dictionary
def storeOffer(offer, direction):

    ID = offer.split(";")[0]
    properties = offer.split(";")[1]

    if direction == "sent":
        offersSent[ID] = properties
    elif direction == "recvd":
        offersRecvd[ID] = properties

# Print all the offers that were sent to customers
def listOffersSent():

    for offer in offersSent:
        print offer, offersSent[offer]

# Print all the offers that were received from providers
def listOffersRecvd():

    for offer in offersRecvd:
        print offer, offersRecvd[offer]

# Delete expired offers
def cleanOffers():

    #if offer expired, remove
    return

# Send an interconnection proposal to an AS
def sendProposal(action):
    # action = propose offerID

    # Get only the offerID
    offerID = action.split("propose ")[1]
    # Get the provider's ASN
    provider = offerID.split("-")[1]

    # If the offer is still valid, send interconnection proposal to the provider
    if checkValidity(offerID) == 1:     
        # Get provider's address
        address = ""
        while ":" not in address:
            address = getAddress(provider)        # Split address into IP and port
        IP = address.split(':')[0]
        port = int(address.split(':')[1])
        # Send interconnection proposal
        msg = "propose"+";"+offerID
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        sendMessage(msg, IP, port)

        # logging
        logs.write(timestamp+";SP;"+offerID+"\n")

    # If the offer is not valid anymore, there is no reason to send the interconnection proposal
    else:
        print "Offer is not valid anymore!"

# Check if the offer is not expired
def checkValidity(offerID):

    # query offersSent[offerID]
    # get expireDate

    # if time.now() < expireDate:
    #    return 1
    # else:
    #   return -1

    return 1

# Receive a propose message and send the contract if the offer is still valid
def establishAgreement(propose):

    offerID = propose.split(";")[1]

    # If offer is still valid, send the contract
    if checkValidity(offerID) == 1:
        sendContract(offerID)
    # Offer is no longer valid
    else:
        msg = "Offer is no longer valid"
        print msg
        # TODO get address
        # Send message
        sendMessage(msg, IP, port)


# Send the contract of the interconnection agreement to the customer
def sendContract(offerID):

    # Get customer's ASN
    customer = offerID.split("-")[0]
    provider = myASN

    # Get provider's address
    address = ""
    while ":" not in address:
        address = getAddress(customer)
    # Split address into IP and port
    IP = address.split(':')[0]
    port = int(address.split(':')[1])

    # Write the contract
    contract = "contract of the Interconnection agreement between "+provider+" and "+customer+offerID
    # Compute the contract hash
    hash_object = hashlib.md5(contract.encode())
    h = hash_object.hexdigest()
    # Provider signs the contract
    cipher = AES.new(myPrivKey,AES.MODE_ECB)   #TODO use a stronger mode in the future
    providerSignature = base64.b64encode(cipher.encrypt(h))

    # Send the contract
    msg = "contract;"+offerID+";"+h+";"+customer+";"+provider+";"+providerSignature
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    sendMessage(msg, IP, port)

    # logging
    logs.write(timestamp+";SC;"+offerID+"\n")

# Customer sign the contract
def signContract(contract):

    # Remove message header
    s = contract.split("contract;")[1]
    # Get the contract hash
    h = contract.split(";")[2]
    # Customer signs the contract
    cipher = AES.new(myPrivKey,AES.MODE_ECB)   #TODO use a stronger mode in the future
    customerSignature = base64.b64encode(cipher.encrypt(h))

    # Get provider's ASN
    provider = contract.split(";")[4]

    # Get provider's address
    address = ""
    while ":" not in address:
        address = getAddress(provider)    # Split address into IP and port
    IP = address.split(':')[0]
    port = int(address.split(':')[1])

    # Send message with the contract signed by the customer
    msg = "publish;"+s+";"+customerSignature
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    sendMessage(msg, IP, port)

    # logging
    logs.write(timestamp+";SS;"+contract.split(";")[1]+"\n")

    key = "IA-"+h
    agreementsCust[key] = myASN+";"+provider

def publishAgreement(info):

    # Get the parameters that will be registered on the ledger 
    contractHash = info.split(";")[2]
    customer = info.split(";")[3]
    provider = myASN
    providerSignature = info.split(";")[5]
    customerSignature = info.split(";")[6]

    key = "IA-"+contractHash 

    # Register the agreement on the ledger
    x = subprocess.check_output('node publish.js registerAgreement \''+key+'\' \''+contractHash+'\' \''+customer+'\' \''+provider+'\' \''+customerSignature+'\' \''+providerSignature+'\''+' '+myUser+' '+ordererIP, shell=True)
    agreementsProv[key] = customer+";"+provider
    print "Success! Updating routing configuration!"

    # Get customer's address
    address = ""
    while ":" not in address:
        address = getAddress(customer)
    # Split address into IP and port
    IP = address.split(':')[0]
    port = int(address.split(':')[1])

    offerID=info.split(";")[1]
    # Send message with the contract signed by the customer
    msg = "ack;"+offerID
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    sendMessage(msg, IP, port)
    # logging
    logs.write(timestamp+";SU;"+offerID+"\n")

def executeAgreements():

    for agmnt in agreementsProv.keys():
        #if ended
        customer = agreementsProv[agmnt].split(";")[0]
        print customer
        # update customer's reputation
        x = subprocess.check_output('node update.js updateCustRep \''+customer+'\' \'1\''+' '+myUser+' '+ordererIP, shell=True)
        print x

        del agreementsProv[agmnt]

    for agmnt in agreementsCust.keys():
        #if ended
        provider = agreementsCust[agmnt].split(";")[1]
        print provider
        # update provider's reputation
        x = subprocess.check_output('node update.js updateProvRep \''+provider+'\' \'1\''+' '+myUser+' '+ordererIP, shell=True)
        print x

        del agreementsCust[agmnt]

    return 

def myAgreements():

    for agmnt in agreementsCust:
        print agmnt, agreementsCust[agmnt]
    for agmnt in agreementsProv:
        print agmnt, agreementsProv[agmnt]


#Main function
if __name__ == "__main__":

    # Generate public and private keys
    basePhrase = myASN+myASN+"Dynam-IX"
    myPubKey = hashlib.md5(basePhrase.encode()).hexdigest() 
    myPrivKey = myPubKey

    # Read intent file
    intents = json.load(open(sys.argv[4]))

    # TODO optimize to not query the blockchain
    # If AS is not registered
    if '{' not in subprocess.check_output('node query.js show \''+myASN+'\''+' '+myUser, shell=True):
        print "Registering new AS", myASN, myAddress, myService
        x = subprocess.check_output('node register.js registerAS \''+myASN+'\' \''+myAddress+'\' \''+myService+'\' \'0\' \'0\' \''+myPubKey+'\''+' '+myUser+' '+ordererIP, shell=True)
        print x
    # else, update address
    else:
        print "Updating AS address", myASN, myAddress, myService
        x = subprocess.check_output('node update.js updateAddress \''+myASN+'\' \''+myAddress+'\''+' '+myUser+' '+ordererIP, shell=True)


    mode = sys.argv[7]

    # Start threads
    threads = []
    if mode == "autonomous":
        t = threading.Thread(target=autonomous)
        threads.append(t)
        t.start()

    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
    t = threading.Thread(target=processMessages)
    threads.append(t)
    t.start()