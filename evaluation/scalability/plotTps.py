#!/usr/bin/python
import sys
import os
import matplotlib
import pylab
import numpy as np

#docker logs orderer.example.com 2>&1|grep "Enqueuing message into batch" | awk -F ' ' '{print $2}'

def plot(file):

    tps = open(file, "r")
    x = []
    y = []

    timestamp = {}

    for line in tps:
        ts = line.split(".")[0]

        if timestamp.has_key(ts):
            timestamp[ts] = timestamp[ts] + 1
        else:
            timestamp[ts] = 1

    tps.close()

    for ts in timestamp:
        print timestamp[ts]

    val = timestamp.values()

    val = map(int, val)

    print np.average(val)
    #pylab.title("Transactions Per Second", fontsize=18)
    #pylab.plot(x, y, linestyle="solid", linewidth=2)
    #pylab.ylabel("Transactions Per Second", fontsize=18)
    #pylab.xlabel("Cumulative number of transactions", fontsize=18)
    #pylab.grid(True)
    #pylab.xlim(0, 20000)
    #pylab.ylim(0, )
    #pylab.legend(loc="best", fontsize=14)
    #pylab.savefig('tps.pdf', dpi=600)
    #pylab.savefig('tps.png', dpi=600)
    #pylab.show() #uncomment to show plots during execution
    #pylab.clf()

#Main function
if __name__ == "__main__":
    file = sys.argv[1]
    plot(file)