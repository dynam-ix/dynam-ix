#!/usr/bin/python
import sys
import os
from datetime import datetime
import numpy as np
import matplotlib
import pylab

transactions = {}

def load(path):

    logs = os.listdir(path)
    # For all logs
    for log in logs:
        if log.endswith(".log") and "AS" in log:
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

   # for key in sorted(transactions):
   #     print key, transactions[key]


def process():
 
    qt = []
    et = []

    for ID in sorted(transactions):
        if len(transactions[ID]) == 12:
            queryTime = datetime.strptime(transactions[ID]["RO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["SQ"], '%Y-%m-%d %H:%M:%S.%f')
            qt.append(queryTime.seconds)
            queryProcess =  datetime.strptime(transactions[ID]["SO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RQ"], '%Y-%m-%d %H:%M:%S.%f')
            queryLatency = queryTime - queryProcess
            establishTime = datetime.strptime(transactions[ID]["RU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["SP"], '%Y-%m-%d %H:%M:%S.%f')
            et.append(establishTime.seconds)
            establishContract = datetime.strptime(transactions[ID]["SC"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RP"], '%Y-%m-%d %H:%M:%S.%f')
            establishSign = datetime.strptime(transactions[ID]["SS"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RC"], '%Y-%m-%d %H:%M:%S.%f')
            establishUpdate = datetime.strptime(transactions[ID]["SU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(transactions[ID]["RS"], '%Y-%m-%d %H:%M:%S.%f')
            establishLatency = establishTime-establishContract-establishSign-establishUpdate

            print ID, queryTime, queryLatency, queryProcess, establishTime, establishContract, establishSign, establishUpdate, establishLatency
    
    print len(qt), len(et)
    print np.average(qt), np.average(et)

    pylab.plot(np.sort(qt),np.arange(len(qt))/float(len(qt)-1), label='query', linestyle="solid", linewidth=2)
    pylab.plot(np.sort(et),np.arange(len(et))/float(len(et)-1), label='establish', linestyle="dashed", linewidth=2)
    pylab.ylabel("Frequency", fontsize=18)
    pylab.xlabel("Time (s)", fontsize=18)
    pylab.grid(True)
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=14)
    pylab.savefig("response.pdf", dpi=600)
    pylab.savefig("response.png", dpi=600)
    #pylab.show() #uncomment to show plots during execution
    pylab.clf()


#Main function
if __name__ == "__main__":

    print sys.argv[1]
    load(sys.argv[1])
    process()