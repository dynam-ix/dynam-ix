#!/usr/bin/python
import sys
import os
import matplotlib
import pylab
import numpy as np

def plot(file):

    size = open(file, "r")
    x = []
    y = []

    for line in size:
        t = line.split(" ")[0]
        s = line.split(" ")[1]

        y.append(float(s)/(1024*1024))

        x.append(int(t))

    size.close()

    print len(x), len(y)

    #pylab.title("Blockchain size x cumulative number of transactions", fontsize=18)
    pylab.plot(x, y, linestyle="solid", linewidth=2)
    pylab.ylabel("Blockchain size (MB)", fontsize=18)
    pylab.xlabel("Cumulative number of transactions", fontsize=18)
    pylab.grid(True)
    pylab.xlim(0, 10000)
    pylab.ylim(0, max(y))
    #pylab.legend(loc="best", fontsize=14)
    pylab.savefig('blockchainSize.pdf', dpi=600)
    pylab.savefig('blockchainSize.png', dpi=600)
    pylab.show() #uncomment to show plots during execution
    pylab.clf()

#Main function
if __name__ == "__main__":
    file = sys.argv[1]
    plot(file)