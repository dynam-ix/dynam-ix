#===================================================#
#                     Imports                       #
#===================================================#
import sys
import os
import socket
import threading
import subprocess
import hashlib
from datetime import datetime

#===================================================#
#                   Global config                   #
#===================================================#
# AS config
myASN = sys.argv[1]
myAddress = sys.argv[2]
myIP = sys.argv[2].split(":")[0]
myPort = sys.argv[2].split(":")[1]
myPubKey = sys.argv[3]      # TODO Generate automatically and store private key on myPrivKey
myService = sys.argv[4]
myPrivKey = ""

# Dictionaries contanining the offers that the AS have sent and received
offersSent = {}
offersRecvd = {}

# Dictionary containing the AS' interconnetion agreements
agreements = {}

#===================================================#
#                     Functions                     #
#===================================================#

# Command line interface. Reads an instructions and call the appropriate function.
def cli():

    while True:
        action = raw_input("Dynam-IX: ")
        if len(action) > 0:
            if "registerAS" in action: # registerAS 'ASN' 'address' 'service' 'custRep' 'provRep' 'pubKey'
                x = subprocess.check_output('node register.js '+action, shell=True)
                print x
            elif "listASes" in action:  # listASes 
                x = subprocess.check_output('node list.js', shell=True)
                print x
            elif "findService" in action: # findService service
                #queryString = "{\"selector\":{\"service\":\"Transit\"}}"
                service = action.split("")[1]
                x = subprocess.check_output('node query.js findService \'{\"selector\":{\"service\":\"'+service+'\"}}\'', shell=True)
                print x
            elif "show" in action: #show 'key'
                x = subprocess.check_output('node query.js '+action, shell=True)
                print x
            elif "history" in action: #history 'key'
                x = subprocess.check_output('node query.js '+action, shell=True)
                print x
            elif "delete" in action: #delete 'key'
                x = subprocess.check_output('node delete.js '+action, shell=True)
                print x
            elif "updateService" in action: #updateService 'ASN' 'newService'
                x = subprocess.check_output('node update.js '+action, shell=True)
                print x
            elif "updateAddress" in action: #updateAddress 'ASN' 'newAddress'
                x = subprocess.check_output('node update.js '+action, shell=True)
                print x
            elif "query" in action: #query providerASN request
                sendQuery(action)
            elif "propose" in action: #propose ID
                sendProposal(action)
            elif "listAgreements" in action:
                x = subprocess.check_output('node listAgreements.js', shell=True)
                print x
            elif "listOffersSent" in action:
                 listOffersSent()
            elif "listOffersRecvd" in action:
                 listOffersRecvd()
            elif "quit" in action:
                 print "Quiting Dynam-IX" 
                 os._exit(1)
            else:
                print "Invalid command\n"

    return

# Receive messages and create threads to process them
def processMessages():

    messageThreads = []

    # Open socket to accept connections
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    serversocket.bind((myIP, int(myPort)))
    serversocket.listen(20) # NOTE We may need to increase the number simultaneous requests 

    while True:
        connection, address = serversocket.accept()
        msg = ''
        msg = connection.recv(1024)     # NOTE We may need to change the amount of received bytes
        if len(msg) > 0:
            if "query" in msg:  # Customer is asking for an offer
                t = threading.Thread(target=sendOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "offer" in msg: # Provider have sent an offer
                t = threading.Thread(target=collectOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "propose" in msg: # Customer is asking to establish an interconnection agreement
                t = threading.Thread(target=establishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "contract" in msg: # Provider have sent the contract to be signed
                t = threading.Thread(target=signContract, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "publish" in msg:  # Customer is sending the signed contract to be registered on the ledger
                t = threading.Thread(target=publishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            else:
                print "Invalid message\n"

# Receives a query action and send it to a potential provider
def sendQuery(action):

    # Get provider's ASN
    provider = action.split(" ")[1]
    # Query the ledger to get the provider's address
    address = getAddress(provider)
    # Split the address into IP and port
    IP = address.split(":")[0]
    port = int(address.split(":")[1])
    # Get the query
    query = action.split(" ")[2]
    # Query the ledger to get the provider's public key
    pubkey = getPubKey(provider)

    # Create the message that is going to be sent
    msg = 'query;'+myASN+';'+query # TODO encrypt with provider's pubkey

    # Send the query to the provider    TODO create a sendMessage(msg, ip, port) function
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((IP, port))
    clientsocket.send(msg)
    clientsocket.close()

# get AS' reputation as a customer or as a provider from the ledger
def getReputation(ASN, role):

    # Query the ledger to get AS' information
    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    # Get the reputation
    if role == "customer":
        return x.split(",")[1].split(':')[1]
    elif role == "provider":
        return x.split(",")[2].split(':')[1]

# get AS' address from the ledger
def getAddress(ASN):

    # Query the ledger to get AS' information
    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    # Get the address
    aux = x.split(",")[0]
    ip = aux.split(":")[1]
    port = aux.split(":")[2]

    # Return ip:port
    return ip.split("\"")[1]+":"+port.split("\"")[0]

# get AS' public key from the ledger
def getPubKey(ASN):

    # Query the ledger to get AS' information
    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    S = x.split(",")[3].split(":")[1]

    return S.split("\"")[1]

# Receive a query from a customer, decide if it is going to answer, and compose and agreement offer 
def sendOffer(query):
    # queryFormat = query;customerASN;properties
    print "Received : "+query

    # Get customer's ASN
    customer = query.split(";")[1]
    # Verify customer's reputation
    reputation = getReputation(customer, "customer")
    # If AS is a good customer, send offer
    if int(reputation) >= 0:                # TODO Define reputation threshold
        # Check interconnection policy to compose and offer to the customer
        offer = composeOffer(query.split(";")[2], customer)
        # If provider can offer something, send
        if len(offer) > 0:
            # Get customer's address
            address = getAddress(customer)
            # Split address into IP and port
            IP = address.split(':')[0]
            port = int(address.split(':')[1])
            # Get customer's public key
            pubKey = getPubKey(customer)
            #Send offer
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect((IP, port))    
            clientsocket.send(offer)    # TODO encrypt with customer's public key
            clientsocket.close()
        # Provider is not able to offer an agreement with the desired properties
        else:
           print "I cannot offer an agreement!"
    # Customer has poor reputation
    else:
        print "Customer with poor reputation!"

# Check the interconnection policy and compose and offer to be sent to the customer
def composeOffer(query, customer):

    # Generate the offer ID
    timestamp = str(datetime.now())
    ID = myASN+"-"+customer+"-"+timestamp

    # TODO create a real offer
    expireDate = "2d"
    offer = "offer;"+ID+";"+query+";10$;"+expireDate

    # Store the offer on the list. This is important to verify if the offer is still valid when the customer sends the proposal message.
    storeOffer(offer, "sent")

    return offer

# Receive an offer and store it on the appropriate dictionary
def collectOffer(offer):
    
    print "Received: "+ offer
    storeOffer(offer, "recvd")

# Store an offer on the appropriate dictionary
def storeOffer(offer, direction):

    ID = offer.split(";")[1]
    properties = offer.split(";")[2]+"-"+offer.split(";")[3]    # TODO fix after defining the intent abstraction

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
    provider = offerID.split("-")[0]

    # If the offer is still valid, send interconnection proposal to the provider
    if checkValidity(offerID) == 1:     
        # Get provider's address
        address = getAddress(provider)
        # Split address into IP and port
        IP = address.split(':')[0]
        port = int(address.split(':')[1])
        # Send interconnection proposal
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((IP, port))    
        clientsocket.send("propose"+";"+offerID)
        clientsocket.close()
    # If the offer is not valid anymore, there is no reason to send the interconnection proposal
    else:
        print "Offer is not valid anymore!"

# Check if the offer is not expired
def checkValidity(offerID):

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
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((address, port))    
        clientsocket.send(msg)
        clientsocket.close()

# Send the contract of the interconnection agreement to the customer
def sendContract(offerID):

    # Get customer's ASN
    customer = offerID.split("-")[1]
    provider = myASN

    # Get provider's address
    address = getAddress(customer)
    # Split address into IP and port
    IP = address.split(':')[0]
    port = int(address.split(':')[1])

    # Write the contract
    contract = "contract of the Interconnection agreement between "+provider+" and "+customer
    # Compute the contract hash
    hash_object = hashlib.md5(contract.encode())
    h = hash_object.hexdigest()
    # Provider sign the contract
    providerSignature = "lalalla" # TODO encrypt hash with provider's private key

    # Send the contract
    msg = "contract;"+offerID+";"+h+";"+customer+";"+provider+";"+providerSignature
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((IP, port))    
    clientsocket.send(msg)
    clientsocket.close()

# Customer sign the contract
def signContract(contract):

    # Remove message header
    s = contract.split("contract;")[1]
    # Get the contract hash
    h = contract.split(";")[2]
    customerSignature = "lelelelele" # TODO use encrypt with AS' private key

    # Get provider's ASN
    provider = contract.split(";")[4]

    # Get provider's address
    address = getAddress(provider)
    # Split address into IP and port
    IP = address.split(':')[0]
    port = int(address.split(':')[1])

    # Send message with the contract signed by the customer
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((IP, port))    
    clientsocket.send("publish;"+s+";"+customerSignature)
    clientsocket.close()


def publishAgreement(info):

    key = "AGR12"   # TODO generate key in an automatically

    # Get the parameters that will be registered on the ledger 
    contractHash = info.split(";")[2]
    customer = info.split(";")[3]
    provider = myASN
    providerSignature = info.split(";")[5]
    customerSignature = info.split(";")[6]

    # Register the agreement on the ledger
    x = subprocess.check_output('node publish.js registerAgreement \''+key+'\' \''+contractHash+'\' \''+customer+'\' \''+provider+'\' \''+customerSignature+'\' \''+providerSignature+'\'', shell=True)

    # TODO store the agreement on the dictionary

    print "Success! Updating routing configuration!"

def executeAgreements():

    return 

#Main function
if __name__ == "__main__":

    # TODO optimize to not query the blockchain
    # If AS is not registered
    if '{' not in subprocess.check_output('node query.js show \''+myASN+'\'', shell=True):
        x = subprocess.check_output('node register.js registerAS \''+myASN+'\' \''+myAddress+'\' \''+myService+'\' \'0\' \'0\' \''+myPubKey+'\'', shell=True)
        print x
    # else, update address
    else:
        x = subprocess.check_output('node update.js updateAddress \''+myASN+'\' \''+myAddress+'\'', shell=True)

    # Start threads
    threads = []
    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
    t = threading.Thread(target=processMessages)
    threads.append(t)
    t.start()