import sys
import threading
import subprocess

def cli():
    while True:
        action = raw_input("Please type your command: ")
        if len(action) > 0:
            if "register" in action: #Register 'ID' 'asn' 'address' 'service' 'custRep' 'provRep'
                x = subprocess.check_output('node register.js '+action, shell=True)
                print x
            elif "list" in action:  #list 
                x = subprocess.check_output('node list.js', shell=True)
                print x
            elif "query" in action: #query 'queryString'
                queryString = "{\"selector\":{\"service\":\"Transit Provider\"}}"
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
            elif "quit" in action:
                return
            else:
                print "Invalid command\n"

    return

def messages():

    print "Hello World!"

    return



#Main function
if __name__ == "__main__":

    threads = []
    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
    t = threading.Thread(target=messages)
    threads.append(t)
    t.start()
