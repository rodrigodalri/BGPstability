#!/usr/bin/env python

import os
import sys
import json
import threading
import subprocess
from datetime import *
#from mrtparse import *



#count ASes and number of occurrences
def countASes(_msglist):

    msglist = _msglist

    ASes = {}
    ASeslist =[]

    for j in msglist:
        ASeslist.append(j["as"])

    ASes = {x:ASeslist.count(x) for x in set(ASeslist)}

    return ASes

#count message type of each AS
def msgAS(_ASnumber, _msglist):

    msglist = _msglist
    ASnumber = _ASnumber

    countWithdrawn = 0
    countAnnouncement = 0

    for i in msglist:
        if ASnumber == i["as"]:
            if i["type"] == 'a':
                countAnnouncement = countAnnouncement + 1
            else:
                countWithdrawn = countWithdrawn +1

    return (countAnnouncement,countWithdrawn)



def main():

    msg = {}
    msglist = []

    with open('routes.txt') as fp:
        line = fp.readline()

        #reading the txt file into memory
        while line:
            type = line.split(";")[0]
            if type == 'w':
                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                prefix = line.split(";")[3]+'/'+ line.split(";")[4]
                msg = {"type": type,"timestamp": timestamp,"as": n_as,"prefix": prefix}
                msglist.append(msg)
            else:
                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                aspath = line.split(";")[3]
                prefix = line.split(";")[4] +'/'+ line.split(";")[5]
                msg = {"type": type,"timestamp": timestamp,"as": n_as,"aspath": aspath,"prefix": prefix}
                msglist.append(msg)

            line = fp.readline()


    #looking for which ASes sent messages
    ASes = countASes(msglist)
    print("ASes found and number of occurrences.")
    print(ASes)
    print("\n")


    #counting the types of messages of each AS
    for i in ASes:
        print("AS: ", i)
        a,w = msgAS(i, msglist)
        print("announcements: ", a)
        print("withdrawns: ", w)
        print("\n")


if __name__ == '__main__':
    main()
