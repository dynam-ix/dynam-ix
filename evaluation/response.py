#!/usr/bin/python
import sys
import os
from datetime import datetime

transactions = {}

def load(path):

    logs = os.listdir(path)
    # For all logs
    for log in logs:
        if log.endswith(".log"):
            l = open(log, "r")
            for line in l:
                timestamp = line.split(";")[0]
                operation = line.split(";")[1]
                ID = line.split(";")[2].replace("\n","")

                # Store the timestamp associated with each operation of a transaction
                if transactions.has_key(ID):
                    transactions[ID][operation] = timestamp
                else:
                    newID = {}
                    newID[operation] = timestamp
                    transactions[ID] = newID

            l.close()

def process():
 
    for ID in transactions:
        queryTime = datetime.strptime(transactions[ID]["RO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["SQ"], '%Y-%m-%d %H:%M:%S.%f')
        queryProcess =  datetime.strptime(transactions[ID]["SO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RQ"], '%Y-%m-%d %H:%M:%S.%f')
        queryLatency = queryTime - queryProcess
        establishTime = datetime.strptime(transactions[ID]["RU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["SP"], '%Y-%m-%d %H:%M:%S.%f')
        establishContract = datetime.strptime(transactions[ID]["SC"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RP"], '%Y-%m-%d %H:%M:%S.%f')
        establishSign = datetime.strptime(transactions[ID]["SS"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RC"], '%Y-%m-%d %H:%M:%S.%f')
        establishUpdate = datetime.strptime(transactions[ID]["SU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RS"], '%Y-%m-%d %H:%M:%S.%f')
        establishLatency = establishTime-establishContract-establishSign-establishUpdate

        print ID, queryTime, queryLatency, queryProcess, establishTime, establishContract, establishSign, establishUpdate, establishLatency


#Main function
if __name__ == "__main__":

    load(sys.argv[1])
    process()