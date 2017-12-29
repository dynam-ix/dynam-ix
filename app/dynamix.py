import sys
import os
import socket
import threading
import subprocess
from datetime import datetime
import hashlib

#AS config
myASN = sys.argv[1]
myAddress = sys.argv[2]
myIP = sys.argv[2].split(":")[0]
myPort = sys.argv[2].split(":")[1]
myPubKey = sys.argv[3]
myService = sys.argv[4]

#Offers lists
offersSent = {}
offersRecvd = {}

#agreements list
agreements = {}

def cli():

    while True:
        action = raw_input("Dynam-IX: ")
        if len(action) > 0:
            if "registerAS" in action: #registerAS 'ASN' 'address' 'service' 'custRep' 'provRep' 'pubKey'
                x = subprocess.check_output('node register.js '+action, shell=True)
                print x
            elif "listASes" in action:  #listAS 
                x = subprocess.check_output('node list.js', shell=True)
                print x
            elif "findService" in action: #findService service
                #queryString = "{\"selector\":{\"service\":\"Transit\"}}"
                service = action.split("")[1]
                #print service
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
            elif "listOffers" in action:
                 listOffers()
            elif "quit" in action:
                 print "Quiting Dynam-IX" 
                 os._exit(1)
            else:
                print "Invalid command\n"

    return

def sendQuery(action):

    ASN = action.split(" ")[1]
    S = getAddress(ASN)
    address = S.split(":")[0]
    port = int(S.split(":")[1])
    query = action.split(" ")[2]
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((address, port))
    pubkey = getPubKey(ASN)
    msg = 'query;'+myASN+';'+query #encrypt with provider's pubkey
    clientsocket.send(msg)
    clientsocket.close()

def getReputation(ASN, role):

    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    if role == "customer":
        return x.split(",")[1].split(':')[1]
    elif role == "provider":
        return x.split(",")[2].split(':')[1]

def getAddress(ASN):

    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    S = x.split(",")[0]
    addr = S.split(":")[1]
    port = S.split(":")[2]

    return addr.split("\"")[1]+":"+port.split("\"")[0]

def getPubKey(ASN):

    x = subprocess.check_output('node query.js show \''+ASN+'\'', shell=True)
    S = x.split(",")[3].split(":")[1]

    return S.split("\"")[1]

def sendOffer(query):

    print "Received query: "+query
    ASN = query.split(";")[1]
    reputation = getReputation(ASN, "customer")
    if int(reputation) >= 0:
        addr = getAddress(ASN)
        address = addr.split(':')[0]
        port = int(addr.split(':')[1])
        pubKey = getPubKey(ASN)
        offer = composeOffer(query.split(";")[2], ASN)
        if len(offer) > 0:
            clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientsocket.connect((address, port))    
            clientsocket.send(offer)
            clientsocket.close()
        else:
           print "I cannot offer an agreement!"
    else:
        print "Customer with poor reputation!"


def composeOffer(query, ASN):

    customer = ASN
    timestamp = str(datetime.now())
    expireDate = "2 days"
    ID = myASN+"-"+customer+"-"+timestamp

    offer = "offer;"+ID+";"+query+";10$"

    storeOffer(offer, "sent")

    return offer

def collectOffer(offer):
    
    print "Received: "+ offer
    storeOffer(offer, "recvd")

def storeOffer(offer, direction):

    ts = offer.split(";")[1]
    properties = offer.split(";")[2]+"-"+offer.split(";")[3]

    if direction == "sent":
        #print "Storing offer sent"
        offersSent[ts] = properties
        #print ts, offersSent[ts]
    elif direction == "recvd":
        #print "Storing offer received"
        offersRecvd[ts] = properties
        #print ts, offersRecvd[ts]


def listOffers():

    print "Offers received\n"
    for offer in offersRecvd:
        print offer, offersRecvd[offer]

    print "Offers sent\n"
    for offer in offersSent:
        print offer, offersSent[offer]

def cleanOffers():

    #if offer expired, remove
    return

def sendProposal(action):

    offerID = action.split("propose ")[1]
    provider = offerID.split("-")[0]

    valid = 1
    #checkValidity(offerID)
    if valid == 1:
        addr = getAddress(provider)
        address = addr.split(':')[0]
        port = int(addr.split(':')[1])

        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((address, port))    
        clientsocket.send("propose"+";"+offerID)
        clientsocket.close()
    else:
        print "Offer is not valid anymore!"

def establishAgreement(offerID):

    valid = 1
    #checkOffer expire data checkOffer(ID)
    if valid == 1:
        sendContract(offerID)
    else:
        msg = "Offer is no longer valid"
        print msg
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((address, port))    
        clientsocket.send(msg)
        clientsocket.close()

def sendContract(proposal):

    #proposal = propose;OfferID

    offerID = proposal.split(";")[1]
    customer = offerID.split("-")[1]
    provider = myASN
    addr = getAddress(customer)
    address = addr.split(':')[0]
    port = int(addr.split(':')[1])
    contract = "contract of the Interconnection agreement between "+provider+" and "+customer
    hash_object = hashlib.md5(contract.encode())
    h = hash_object.hexdigest()
    providerSignature = "lalalla" #use encrypt with AS' private key

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((address, port))    
    clientsocket.send("contract;"+offerID+";"+h+";"+customer+";"+provider+";"+providerSignature)
    clientsocket.close()

def signContract(contract):

    s = contract.split("contract;")[1]
    #check contract
    terms = contract.split(";")[2]
    customerSignature = "lelelelele" #use encrypt with AS' private key

    provider = contract.split(";")[4]

    addr = getAddress(provider)
    address = addr.split(':')[0]
    port = int(addr.split(':')[1])

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((address, port))    
    clientsocket.send("publish;"+s+";"+customerSignature)
    clientsocket.close()

    return

def publishAgreement(info):

    print info

    key = "AGR10"
    contractHash = info.split(";")[2]
    customer = info.split(";")[3]
    provider = myASN
    providerSignature = info.split(";")[5]
    customerSignature = info.split(";")[6]

    #agreemeent ID, contractHash, customerASN, providerASN(myASN), customerSignature, providerSignature
    x = subprocess.check_output('node publish.js storeAgreement \''+key+'\' \''+contractHash+'\' \''+customer+'\' \''+provider+'\' \''+customerSignature+'\' \''+providerSignature+'\'', shell=True)

    print "Success! Updating routing configuration!"


def executeAgreements():

    return 

def processMessages():

    messageThreads = []

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    serversocket.bind((myIP, int(myPort)))
    serversocket.listen(20) #maximum of 20 simultaneous requests 

    while True:
        connection, address = serversocket.accept()
        msg = ''
        msg = connection.recv(1024)
        if len(msg) > 0:
            if "query" in msg:
                t = threading.Thread(target=sendOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "offer" in msg:
                t = threading.Thread(target=collectOffer, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "propose" in msg:
                t = threading.Thread(target=establishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "contract" in msg:
                t = threading.Thread(target=signContract, args=(msg,))
                messageThreads.append(t)
                t.start()
            elif "publish" in msg:
                t = threading.Thread(target=publishAgreement, args=(msg,))
                messageThreads.append(t)
                t.start()
            else:
                print "Invalid message\n"

#Main function
if __name__ == "__main__":

    #optimize to not query the blockchain
    #If AS is not registered
    if '{' not in subprocess.check_output('node query.js show \''+myASN+'\'', shell=True):
        x = subprocess.check_output('node register.js registerAS \''+myASN+'\' \''+myAddress+'\' \''+myService+'\' \'0\' \'0\' \''+myPubKey+'\'', shell=True)
        print x
    #else, update address
    else:
        x = subprocess.check_output('node update.js updateAddress \''+myASN+'\' \''+myAddress+'\'', shell=True)

    threads = []
    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
    t = threading.Thread(target=processMessages)
    threads.append(t)
    t.start()