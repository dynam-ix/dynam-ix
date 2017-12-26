import sys
import os
import socket
import threading
import subprocess

def cli():
    while True:
        action = raw_input("Dynam-IX: ")
        if len(action) > 0:
            if "register" in action: #Register 'ID' 'asn' 'address' 'service' 'custRep' 'provRep'
                x = subprocess.check_output('node register.js '+action, shell=True)
                print x
            elif "list" in action:  #list 
                x = subprocess.check_output('node list.js', shell=True)
                print x
            elif "query" in action: #query 'queryString'
                queryString = "{\"selector\":{\"service\":\"cloud\"}}"
                x = subprocess.check_output('node query.js '+action, shell=True)
                print x
            elif "history" in action: #history 'ID'
                x = subprocess.check_output('node query.js '+action, shell=True)
                print x
            elif "delete" in action: #delete 'ID'
                x = subprocess.check_output('node delete.js '+action, shell=True)
                print x
            elif "updateService" in action: #updateService 'ID' 'newService'
                x = subprocess.check_output('node update.js '+action, shell=True)
                print x
            elif "updateAddress" in action: #updateAddress 'ID' 'newAddress'
                x = subprocess.check_output('node update.js '+action, shell=True)
                print x
            elif "propose" in action: 
                S = action.split(" ")[1]
                address = S.split(":")[0]
                port = int(S.split(":")[1])
                clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientsocket.connect((address, port))
                msg = 'proposal:5000'
                clientsocket.send(msg)
                clientsocket.close()
            elif "quit" or "exit" in action:
                 os._exit(1)
            else:
                print "Invalid command\n"

    return

def sendOffer():
    print "\nI will check if I can send an offer\n"
#      reputation = verifyReputation(m.ASN):
#      if reputation >= threshold:
#        offer = checkPolicy(P, reputation) #can be based on the reputation
#        if offer not "NULL"
#            sendOffer()  
    return 

def establishAgreement():
    print "\nI will check if the proposal is still valid\n"
 #     if checkValidity(m):
 #           createSmartContract()
 #           publishSmartContract()
 #           updateNetworkConfiguration()
 #    else:
 #           sendMessage("This offer is not valid anymore!")
    return

def collectOffer():
    print "\nCollecting offer\n"
#    if checkValidity(m):
#          storeOffer(m)
#    if numOffers == X:
        #select and send proposal
    return

def processMessages():

    messageThreads = []

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', int(sys.argv[1]))) #load from config
    serversocket.listen(5) # become a server socket, maximum 5 connections

    while True:
        connection, address = serversocket.accept()
        msg = connection.recv(1024)
        if len(msg) > 0:
            if msg == "query":
                t = threading.Thread(target=sendOffer)
                messageThreads.append(t)
                t.start()
            elif "proposal" in msg:
                t = threading.Thread(target=establishAgreement)
                messageThreads.append(t)
                t.start()
            elif msg == "offer":
                t = threading.Thread(target=collectOffer)
                messageThreads.append(t)
                t.start()
            else:
                print "Invalid message\n"

    return

#Main function
if __name__ == "__main__":

    threads = []
    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
    t = threading.Thread(target=processMessages)
    threads.append(t)
    t.start()
