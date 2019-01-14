#!/usr/bin/env python

import os
import sys
import json
import threading
import subprocess
from datetime import *
#from mrtparse import *


#read the txt file into memory
def txttoMemory():

    msg = {}
    msglist = []

    with open('routes.txt') as fp:
        line = fp.readline()

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

    return msglist

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

#count Prefix and number of occurrences
def countPrefix(_msglist):

    msglist = _msglist

    prefix = {}
    prefixList =[]

    for j in msglist:
        prefixList.append(j["prefix"])

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#count message type of each prefix
def msgPrefix(_prefix, _msglist):

    msglist = _msglist
    prefix = _prefix

    countWithdrawn = 0
    countAnnouncement = 0

    for i in msglist:
        if prefix == i["prefix"]:
            if i["type"] == 'a':
                countAnnouncement = countAnnouncement + 1
            else:
                countWithdrawn = countWithdrawn +1

    return (countAnnouncement,countWithdrawn)

#list every aspath from this prefix
def msgASPath(_prefix, _msglist):

    msglist = _msglist
    prefix = _prefix
    aspathList = []

    for i in msglist:
        if prefix == i["prefix"] and i["type"] == 'a':
            aspathList.append(i["timestamp"]+" : "+i["as"]+" : "+i["aspath"])

    return aspathList


def main():

    #reading the txt file into memory
    msglist = txttoMemory()

    #looking for which ASes sent messages
    ASes = countASes(msglist)
    print("ASes found and number of occurrences.")
    print(ASes)
    print("\n")


    #counting the types of messages of each AS
    for i in ASes:
        print("AS: %s" % i)
        a,w = msgAS(i, msglist)
        print("announcements: %s" % a)
        print("withdrawns: %s" % w)
        print("\n")


    #looking for which prefix
    prefixes = countPrefix(msglist)
    print("Prefixes found and number of occurrences.")
    print(prefixes)
    print("\n")


    #counting the types of messages of each prefix
    for i in prefixes:
        print("Prefix: %s" % i)
        a,w = msgPrefix(i, msglist)
        print("announcements: %s" % a)
        print("withdrawns: %s" % w)
        print("\n")

    #list every aspath from every prefix
    for i in prefixes:
        print("Prefix: %s" % i)
        print("Timestamp : AS : ASpath")
        aspathList = msgASPath(i,msglist)
        for j in aspathList:
            print(j)
        print("\n")

if __name__ == '__main__':
    main()
