#!/usr/bin/python

import urllib, json

prefixes = []

def getASes():
    output = open("ases.list", "w")

    for pageNum in range(1, 168):
        print pageNum
        url = "http://as-rank.caida.org/api/v1/asns?page="+str(pageNum)
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        for AS in data['data']:
            output.write(AS+'\n')

    output.close()

def getPrefixes(file):

    f = open(file, "r")
    prefix = open("prefixes.count", "a")

    i = 1
    for AS in f:
        print i
        url = "http://as-rank.caida.org/api/v1/asns/"+AS
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        if data['data']['cone'].get('prefixes'):
            prefix.write(AS.strip()+";"+str(data['data']['cone']['prefixes'])+";"+str(data['data']['cone']['addresses'])+"\n")
        else:
            print 'AS '+AS+" has no cone"

        i = i + 1

    f.close()
    prefix.close()

#Main function
if __name__ == "__main__":
    getPrefixes("ases2.list")