#!/usr/bin/python
import sys
import os
from datetime import datetime
import numpy as np
import matplotlib
import pylab

t = {}

def load(path):

    experiments =  os.walk(path).next()[1]
    for experiment in experiments:
        transactions = {} 
        logs = os.listdir(path+"/"+experiment)
        # For all logs
        for log in logs:
            if log.endswith(".log") and "AS" in log:
                l = open(path+"/"+experiment+"/"+log, "r")
                for line in l:
                    try:
                        timestamp = line.split(";")[0]
                    except IndexError:
#                        print line
                        continue

                    try:
                        operation = line.split(";")[1]
                    except IndexError:
 #                       print line
                        continue

                    try:
                        ID = line.split(";")[2].replace("\n","")
                    except IndexError:
  #                      print line
                        continue

                    # Store the timestamp associated with each operation of a transaction
                    if transactions.has_key(ID):
                        transactions[ID][operation] = timestamp
                    else:
                        newID = {}
                        newID[operation] = timestamp
                        transactions[ID] = newID

                l.close()
        t[experiment] = transactions
    #for key in sorted(transactions):
    #    print key, transactions[key]

    print t.keys()

def process():
 
    linestyles = ['-', '--', '-.', ':']
    x = 0
    keys = map(int, t.keys())

    for e in sorted(keys):
        qt = []
        et = []
        ct = []
        tt = []
        exp = str(e)

        for ID in sorted(t[exp]):
            #print len(t[ID]) 
            if len(t[exp][ID]) == 13:
                queryTime = datetime.strptime(t[exp][ID]["RO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["SQ"], '%Y-%m-%d %H:%M:%S.%f')
                queryProcess =  datetime.strptime(t[exp][ID]["SO"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["RQ"], '%Y-%m-%d %H:%M:%S.%f')
                queryLatency = queryTime - queryProcess
                establishTime = datetime.strptime(t[exp][ID]["RU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["SP"], '%Y-%m-%d %H:%M:%S.%f')
                establishContract = datetime.strptime(t[exp][ID]["SC"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["RP"], '%Y-%m-%d %H:%M:%S.%f')
                establishSign = datetime.strptime(t[exp][ID]["SS"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["RC"], '%Y-%m-%d %H:%M:%S.%f')
                establishUpdate = datetime.strptime(t[exp][ID]["SU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["RS"], '%Y-%m-%d %H:%M:%S.%f')
                establishLatency = establishTime-establishContract-establishSign-establishUpdate
                confirmTime = datetime.strptime(t[exp][ID]["VU"], '%Y-%m-%d %H:%M:%S.%f') - datetime.strptime(t[exp][ID]["RU"], '%Y-%m-%d %H:%M:%S.%f')

                #print ID, queryTime, queryLatency, queryProcess, establishTime, establishContract, establishSign, establishUpdate, establishLatency, confirmTime
                if confirmTime.seconds > 25:
                    #print ID, t[exp][ID]
                    i = 1
                else:
                    et.append(establishTime.seconds)
                    ct.append(confirmTime.seconds)
                    tt.append(confirmTime.seconds+establishTime.seconds)
                    qt.append(queryTime.seconds)

        print len(qt), len(et), len(tt)
        print np.std(qt), np.std(et), np.std(tt)
#        print max(qt), max(et), max(tt)
 
        pylab.plot(np.sort(qt),np.arange(len(qt))/float(len(qt)-1), label=exp.split("-")[0]+" ASes", linestyle=linestyles[x%4], linewidth=2)
#        pylab.plot(np.sort(et),np.arange(len(et))/float(len(et)-1), label=exp.split("-")[0]+" ASes", linestyle=linestyles[x%4], linewidth=2)
#        pylab.plot(np.sort(tt),np.arange(len(tt))/float(len(tt)-1), label='confirm', linestyle="dotted", linewidth=2)
        x = x + 1

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

    load(sys.argv[1])
    process()