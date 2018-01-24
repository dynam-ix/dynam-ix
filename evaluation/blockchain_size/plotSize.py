#!/usr/bin/python
import sys
import os
import matplotlib.pyplot as plt
import pylab
import numpy as np

def plot(path):

    plt.figure()
    plt.yscale('log')

    files = os.listdir(path)
    for file in files:
        if ".log" in file:

            size = open(path+file, "r")
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
            plt.plot(x, y, linestyle="solid", linewidth=2, label=file.split(".log")[0])


    plt.ylabel("Blockchain size (MB)", fontsize=18)
    plt.xlabel("Cumulative number of transactions", fontsize=18)
    plt.grid(True)
    plt.xlim(0, 10000)
    plt.ylim(0, )
    plt.legend(loc="best", ncol=2)
    plt.savefig('blockchainSize.pdf', dpi=600)
    plt.savefig('blockchainSize.png', dpi=600)
    plt.show() #uncomment to show plots during execution
    plt.clf()

#Main function
if __name__ == "__main__":
    path = sys.argv[1]
    plot(path)