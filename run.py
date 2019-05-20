#!/usr/bin/env python
import os
import sys
import copy
import json
import time
#import pylab
import ipaddress
import threading
import subprocess
#import numpy as np
from datetime import *
#import matplotlib.pyplot as plt
#import matplotlib.dates as mdates
from collections import defaultdict
#plt.rcParams.update({'figure.max_open_warning': 0})

#AS43252 is decix
#AS62972 is amsix
#AS24115 is equinix
#AS8714 is equinix
#TODO some plots are out of date

def pair_of_lists():
    return [[], []]

#-----------------------------[FILE]----------------------------------------------
# "_new" functions are more efficient versions
#read the txt file into memory
def txttoMemory(_path):

    msg = {}
    msglist = []
    path = _path

    with open(path) as fp:
        line = fp.readline()

        while line:
            type = line.split(";")[0]
            if type == 'w':
                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                list = line.split(";")
                prefix = list[3]+";"+list[4]
                i = 5
                try:
                    while "\n" != list[i]:
                        try:
                            prefix = prefix+";"+list[i]+";"+list[i+1]
                            i = i + 2
                        except:
                            a = 0
                except:
                        a = 0
                if prefix[:-1] == ";":
                    prefix = prefix[:-1]
                    print("entrou")
                    print(prefix)
                msg = {"type": type,"timestamp": timestamp,"as": n_as,"prefix": prefix}
                msglist.append(msg)
            else:
                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                aspath = line.split(";")[3]
                prefix = line.split(";")[4] +';'+ line.split(";")[5]
                msg = {"type": type,"timestamp": timestamp,"as": n_as,"aspath": aspath,"prefix": prefix}
                msglist.append(msg)

            line = fp.readline()

    return msglist

#read the txt file into memory
def txttoMemory_new(_path, _collectorName):

    msg = {}
    msgList = []
    asesList = []
    prefixesList = []
    path = _path
    collectorName = _collectorName
    specialCase = {}
    highTimestampA = {}
    highTimestampW = {}


    prefixListA =[]
    prefixListW =[]
    prefixList =[]
    countWithdrawn = 0
    countAnnouncement = 0
    count = 0
    totalMSG = 0
    announcement = 0
    withdrawn = 0


    # A, W
    data = defaultdict(pair_of_lists)

    with open(path) as fp:
        line = fp.readline()

        while line:
            type = line.split(";")[0]
            if type == 'w':
                withdrawn = withdrawn + 1

                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                list2 = line.split(";")
                prefix = list2[3]+";"+list2[4]
                i = 5
                try:
                    while "\n" != list2[i]:
                        try:
                            prefix = prefix+";"+list2[i]+";"+list2[i+1]
                            i = i + 2
                        except:
                            a = 0
                except:
                        a = 0
                if prefix[:-1] == ";":
                    prefix = prefix[:-1]
                msg = {"type": type, "timestamp": timestamp, "as": n_as, "prefix": prefix}
                if(isMsgNew_new(data,int(n_as),msg,specialCase,highTimestampA,highTimestampW)):
                    data[int(n_as)][1].append(msg)
                    highTimestampW[str(prefix)] = int(timestamp)
                list3 = prefix.split(';')
                for k in range(0,len(list3)-1,2):
                    prefixesList.append(list3[k]+';'+list3[k+1])
                    prefixList.append(list3[k]+';'+list3[k+1])
                    prefixListW.append(list3[k]+';'+list3[k+1])
                asesList.append(int(n_as))
                msgList.append(msg)

            else:
                announcement = announcement + 1
                timestamp = line.split(";")[1]
                n_as = line.split(";")[2]
                aspath = line.split(";")[3]
                prefix = line.split(";")[4] +';'+ line.split(";")[5]
                msg = {"type": type,"timestamp": timestamp,"as": n_as,"aspath": aspath,"prefix": prefix}
                prefixesList.append(prefix)
                prefixList.append(prefix)
                prefixListA.append(prefix)
                if (n_as == '43252' or n_as == '62972'):
                    list4 = aspath.split(',')[0]
                    try:
                        asesList.append(int(list4[2:-1]))
                        if(isMsgNew_new(data,int(list4[2:-1]),msg,specialCase,highTimestampA,highTimestampW)):
                            specialCase[str(prefix)] = int(list4[2:-1])
                            highTimestampA[str(prefix)] = int(timestamp)
                            data[int(list4[2:-1])][0].append(msg)
                    except:
                        asesList.append(int(list4[2:-2]))
                        if(isMsgNew_new(data,int(list4[2:-2]),msg,specialCase,highTimestampA,highTimestampW)):
                            specialCase[str(prefix)] = int(list4[2:-2])
                            highTimestampA[str(prefix)] = int(timestamp)
                            data[int(list4[2:-2])][0].append(msg)
                else:
                    asesList.append(int(n_as))
                    if(isMsgNew_new(data,int(n_as),msg,specialCase,highTimestampA,highTimestampW)):
                        data[int(n_as)][0].append(msg)
                        highTimestampA[str(prefix)] = int(timestamp)

                msgList.append(msg)

            line = fp.readline()

    #print(specialCase)
    #print(highTimestampA)
    #print(highTimestampW)

    count = {x:prefixList.count(x) for x in set(prefixList)}
    countAnnouncement = {x:prefixListA.count(x) for x in set(prefixListA)}
    countWithdrawn = {x:prefixListW.count(x) for x in set(prefixListW)}
    count = len(count)
    countAnnouncement = len(countAnnouncement)
    countWithdrawn = len(countWithdrawn)
    totalMSG = announcement + withdrawn

    txtIXP(totalMSG,announcement,withdrawn,count,countAnnouncement,countWithdrawn,collectorName)

    return msgList,asesList,prefixesList,data

#test if msg is not duplicated
def isMsgNew(_data, _nas, _msg, _specialCase):

    data = _data
    nas = _nas
    msg = _msg
    specialCase = _specialCase
    find = 0
    new = 0
    timestampW = 0
    timestampA = 0

    if int(nas) in data.keys():

        #announcement message
        if (msg["type"] == 'a'):
            #run in list of announcements
            for i in data[nas][0]:
                if (i["prefix"] == msg["prefix"]):
                    find = 1
                    if len(data[nas][1]) > 0 or msg["as"] == str(nas):
                        #run in list of Withdrawns
                        for j in data[nas][1]:
                            #highest timestamp W
                            if (j["prefix"] == msg["prefix"] and int(j["timestamp"]) > int(timestampW)):
                                timestampW = int(j["timestamp"])
                            else:
                                timestampW = timestampW
                        for l in data[nas][0]:
                            #highest timestamp A
                            if (l["prefix"] == msg["prefix"] and int(l["timestamp"]) > int(timestampA)):
                                timestampA = int(l["timestamp"])
                            else:
                                timestampA = timestampA
                        if (int(msg["timestamp"])>timestampW and timestampW > timestampA):
                            new = 1
                        else:
                            new = 0
                    #route collector = AS
                    else:
                        if len(data[int(msg["as"])][1]) > 0:
                            #run in list of Withdrawns
                            for k in data[int(msg["as"])][1]:
                                #highest timestamp W
                                if (str(k["prefix"]) == str(msg["prefix"]) and int(k["timestamp"]) > int(timestampW)):
                                    timestampW = int(k["timestamp"])
                                else:
                                    timestampW = timestampW
                            for j in data[nas][0]:
                                #highest timestamp A
                                if (str(j["prefix"]) == str(msg["prefix"]) and int(j["timestamp"]) > int(timestampA)):
                                    timestampA = int(j["timestamp"])
                                else:
                                    timestampA = timestampA
                            if (int(msg["timestamp"])>int(timestampW) and timestampW > timestampA):
                                new = 1
                            else:
                                new = 0
            if (find == 0):
                new = 1

        #withdrawn message
        else:
            if(len(data[nas][0]) > 0):
                for i in data[nas][1]:
                    if (i["prefix"] == msg["prefix"]):
                        find = 1
                        for k in data[nas][0]:
                            if (str(k["prefix"]) == str(msg["prefix"]) and int(k["timestamp"]) > int(timestampA)):
                                timestampA = int(k["timestamp"])
                            else:
                                timestampA = timestampA
                        for j in data[nas][1]:
                            if (str(j["prefix"]) == str(msg["prefix"]) and int(j["timestamp"]) > int(timestampW)):
                                timestampW = int(j["timestamp"])
                            else:
                                timestampW = timestampW
                        if (int(msg["timestamp"])>int(timestampW) and timestampA > timestampW):
                            new = 1
                        else:
                            new = 0
                if (find == 0):
                    new = 1

            #route collector = AS
            else:
                if msg["prefix"] in specialCase.keys():
                    realAS = specialCase[msg["prefix"]]
                    for i in data[nas][1]:
                        if (i["prefix"] == msg["prefix"]):
                            find = 1
                            for k in data[realAS][0]:
                                if (str(k["prefix"]) == str(msg["prefix"]) and int(k["timestamp"]) > int(timestampA)):
                                    timestampA = int(k["timestamp"])
                                else:
                                    timestampA = timestampA
                            for j in data[nas][1]:
                                if (str(j["prefix"]) == str(msg["prefix"]) and int(j["timestamp"]) > int(timestampW)):
                                    timestampW = int(j["timestamp"])
                                else:
                                    timestampW = timestampW
                            if (int(msg["timestamp"])>int(timestampW) and timestampA > timestampW):
                                new = 1
                            else:
                                new = 0
                    if (find == 0):
                        new = 1

    #first msg of AS
    else:
        new = 1

    return new

#test if msg is not duplicated
def isMsgNew_new(_data, _nas, _msg, _specialCase, _highTimestampA, _highTimestampW):

    data = _data
    nas = _nas
    msg = _msg
    specialCase = _specialCase
    highTimestampA = _highTimestampA
    highTimestampW = _highTimestampW
    timestampW = 0
    timestampA = 0
    new = 0

    if msg["prefix"] in highTimestampA.keys():
        timestampA = int(highTimestampA[msg["prefix"]])
    if msg["prefix"] in highTimestampW.keys():
        timestampW = int(highTimestampW[msg["prefix"]])


    #announcement message
    if msg["type"] == 'a':
        if timestampA > 0:
            if timestampW > timestampA and int(msg["timestamp"]) > timestampW:
                new = 1
            else:
                new = 0
        else:
            new = 1

    #withdrawn message
    else:
        if timestampW > 0:
            if timestampA > timestampW and int(msg["timestamp"]) > timestampA:
                new = 1
            else:
                new = 0
        else:
            new = 1

    #print(new)
    return new

#save in a txt file information about the prefix
def txtPrefix(_prefix, _numASes, _numChanges, _label):

    prefix = _prefix
    numASes = _numASes
    numChanges = _numChanges
    label = _label

    f = open('reports/prefixes'+label+'.txt', 'a+')
    #FORMAT: prefix;number_of_ases;number_of_changes
    f.write(str(prefix)+';'+str(numASes)+';'+str(numChanges)+'\n')
    f.close()

#save in a txt file information about the prefix:AS
def txtPrefix2(_prefix, _asn, _numChanges, _label):

    prefix = _prefix
    numChanges = _numChanges
    label = _label
    asn = _asn

    f = open(str(label)+'/reportprefixesASes.txt', 'a+')
    #FORMAT: prefix;asn;number_of_changes
    f.write(str(prefix)+';'+str(asn)+';'+str(numChanges)+'\n')
    f.close()

#save in a txt file information about the IXP
def txtIXP(_totalMSG, _announcement, _withdrawn, _prefix, _prefixA, _prefixW, _collectorName):

    totalMSG = _totalMSG
    announcement = _announcement
    withdrawn = _withdrawn
    prefix = _prefix
    prefixA = _prefixA
    prefixW = _prefixW
    collectorName = _collectorName

    f = open(str(collectorName)+'/reportIXP.txt', 'a+')
    #FORMAT: total_number_of_messages;number_of_announcements;number_of_withdrawns;total_number_of_prefixes;announced_prefixes;withdrawed_prefixes
    f.write(str(totalMSG)+';'+str(announcement)+';'+str(withdrawn)+';'+str(prefix)+';'+str(prefixA)+';'+str(prefixW)+'\n')
    f.close()

#save in a txt file information about the IXP
def txtIXP2(_list, _collectorName):

    list = _list
    collectorName = _collectorName

    f = open(str(collectorName)+'/reportIXP.txt', 'a+')
    f.write('ASes:'+'\n')
    for i in list:
        f.write(str(i)+'\n')
    f.close()

#save in a txt file information about the AS
def txtAS(_label, _msgA, _msgW, _prefix, _prefixA, _prefixW, _collectorName):

    label = _label
    msgA = _msgA
    msgW = _msgW
    prefix = _prefix
    prefixA = _prefixA
    prefixW = _prefixW
    collectorName = _collectorName

    label = str(collectorName)+'/reportAS'+str(label)+'.txt'
    f = open(label, 'a+')
    #FORMAT: total_number_of_messages;number_of_announcements;number_of_withdrawns;total_number_of_prefixes;announced_prefixes;withdrawed_prefixes
    f.write(str(msgA+msgW)+';'+str(msgA)+';'+str(msgW)+';'+str(prefix)+';'+str(prefixA)+';'+str(prefixW)+'\n')
    f.close()
#-----------------------------[FILE]----------------------------------------------
#-------------------------------[AS]----------------------------------------------
#count ASes and number of occurrences
def countASes(_msglist):

    msglist = _msglist

    ASes = {}
    ASeslist =[]

    for j in msglist:
        if (j["as"] == '43252' or j["as"] == '62972') and j["type"] == 'a':
            list = j["aspath"].split(',')[0]
            try:
                ASeslist.append(int(list[2:-1]))
            except:
                ASeslist.append(int(list[2:-2]))
        else:
            ASeslist.append(int(j["as"]))


    ASes = {x:ASeslist.count(x) for x in set(ASeslist)}

    return ASes

#count message type of each AS
def msgAS(_ASnumber, _msglist):

    msglist = _msglist
    ASnumber = _ASnumber

    countWithdrawn = 0
    countAnnouncement = 0

    for i in msglist:
        if (i["as"] == '43252' or i["as"] == '62972') and i["type"] == 'a':
            list = i["aspath"].split(',')[0]
            try:
                var = int(list[2:-1])
            except:
                var = int(list[2:-2])
            if ASnumber == var:
                if i["type"] == 'a':
                    countAnnouncement = countAnnouncement + 1
                else:
                    countWithdrawn = countWithdrawn + 1
        else:
            if str(ASnumber) == i["as"]:
                if i["type"] == 'a':
                    countAnnouncement = countAnnouncement + 1
                else:
                    countWithdrawn = countWithdrawn + 1

    return (countAnnouncement,countWithdrawn)

#count the number of prefixes of each AS
def prefixAS(_ASnumber, _msglist):

    msglist = _msglist
    ASnumber = _ASnumber

    prefixListA =[]
    prefixListW =[]
    prefixList =[]

    countWithdrawn = 0
    countAnnouncement = 0
    count = 0

    for i in msglist:
        if (i["as"] == '43252' or i["as"] == '62972') and i["type"] == 'a':
            list = i["aspath"].split(',')[0]
            try:
                var = int(list[2:-1])
            except:
                var = int(list[2:-2])
            if ASnumber == var:
                if i["type"] == 'a':
                    list = i["prefix"].split(';')
                    for k in range(0,len(list)-1,2):
                        prefixList.append(list[k]+';'+list[k+1])
                        prefixListA.append(list[k]+';'+list[k+1])
                else:
                    list = i["prefix"].split(';')
                    for j in range(0,len(list)-1,2):
                        prefixList.append(list[j]+';'+list[j+1])
                        prefixListW.append(list[j]+';'+list[j+1])
        else:
            if str(ASnumber) == i["as"]:
                if i["type"] == 'a':
                    list = i["prefix"].split(';')
                    for k in range(0,len(list)-1,2):
                        prefixList.append(list[k]+';'+list[k+1])
                        prefixListA.append(list[k]+';'+list[k+1])
                else:
                    list = i["prefix"].split(';')
                    for j in range(0,len(list)-1,2):
                        prefixList.append(list[j]+';'+list[j+1])
                        prefixListW.append(list[j]+';'+list[j+1])


    count = {x:prefixList.count(x) for x in set(prefixList)}
    countAnnouncement = {x:prefixListA.count(x) for x in set(prefixListA)}
    countWithdrawn = {x:prefixListW.count(x) for x in set(prefixListW)}

    count = len(count)
    countAnnouncement = len(countAnnouncement)
    countWithdrawn = len(countWithdrawn)

    return (count,countAnnouncement,countWithdrawn)

#count the number of msg
def reportAS(_data, _collectorName):

    data = _data
    collectorName = _collectorName

    #TODO count prefixes
    for i in data:
        msgA = len(data[i][0])
        msgW = len(data[i][1])
        txtAS(i,msgA,msgW,0,0,0,collectorName)
#-------------------------------[AS]----------------------------------------------
#------------------------------[PREFIX]-------------------------------------------
#count the number of prefixes of IXP
def prefixIXP(_msglist):

    msglist = _msglist

    prefixListA =[]
    prefixListW =[]
    prefixList =[]

    countWithdrawn = 0
    countAnnouncement = 0
    count = 0

    for i in msglist:
        if i["type"] == 'a':
            list = i["prefix"].split(';')
            for k in range(0,len(list)-1,2):
                prefixList.append(list[k]+';'+list[k+1])
                prefixListA.append(list[k]+';'+list[k+1])
        else:
            list = i["prefix"].split(';')
            for j in range(0,len(list)-1,2):
                prefixList.append(list[j]+';'+list[j+1])
                prefixListW.append(list[j]+';'+list[j+1])


    count = {x:prefixList.count(x) for x in set(prefixList)}
    countAnnouncement = {x:prefixListA.count(x) for x in set(prefixListA)}
    countWithdrawn = {x:prefixListW.count(x) for x in set(prefixListW)}

    count = len(count)
    countAnnouncement = len(countAnnouncement)
    countWithdrawn = len(countWithdrawn)

    return (count,countAnnouncement,countWithdrawn)

#count Prefix and number of occurrences
def countPrefix(_msglist):

    msglist = _msglist

    prefix = {}
    prefixList =[]

    for i in msglist:
        list = i["prefix"].split(';')
        for k in range(0,len(list)-1,2):
            prefixList.append(list[k]+';'+list[k+1])

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#count message type of each prefix
def msgPrefix(_prefix, _msglist):

    msglist = _msglist
    prefix = _prefix

    countWithdrawn = 0
    countAnnouncement = 0

    for i in msglist:
        list = i["prefix"].split(';')
        for k in range(0,len(list)-1,2):
            if prefix == list[k]+';'+list[k+1]:
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

#test if the networks overlaps
def isAggregate(_prefix1, _prefix2):

    prefix1 = _prefix1
    prefix2 = _prefix2

    prefix1 = prefix1.replace(";", "/")
    prefix2 = prefix2.replace(";", "/")

    network1 = ipaddress.ip_network(prefix1)
    network2 = ipaddress.ip_network(prefix2)


    #TODO:
    #1 > 2 return 1
    #2 > 1 return 2
    #print('entrou')

    #if network1.overlaps(network2):
    #    return 1
    #else:
    #    return 0
    if network1.version == network2.version:
        if network1.supernet_of(network2):
            return 1
        elif network2.supernet_of(network1):
            return 2
        else:
            return 0
    else:
        return 0

#count prefix changes
def prefixChanges(_prefix, _prefixes, _msglist):

    prefix = _prefix
    prefixes = _prefixes
    msglist = _msglist

    list = []
    changesList = []
    asesList = []

    for i in prefixes:
        if prefix == i:
            list = msgASPath(i,msglist)
            for j in list:
                if j.split(':')[1] == '43252' or j.split(':')[1] == '62972':
                    list = j["aspath"].split(',')[0]
                    try:
                        asesList.append(int(list[2:-1]))
                    except:
                        asesList.append(int(list[2:-2]))
                else:
                    asesList.append(j.split(':')[1])
                changesList.append(j.split(':')[2])

    return({x:asesList.count(x) for x in set(asesList)},{y:changesList.count(y) for y in set(changesList)})

#count prefix:AS changes
def prefixASChanges(_prefix, _asn, _prefixes, _msglist):

    prefix = _prefix
    prefixes = _prefixes
    msglist = _msglist
    asn = _asn

    var = 0
    list = []
    changesList = []

    for i in prefixes:
        if prefix == i:
            list = msgASPath(i,msglist)
            for j in list:
                test = j.split(':')[1]
                if int(test[1:]) == int('43252') or int(test[1:]) == int('62972'):
                    var = list[0].split(':')[2]
                    var = var.split(',')[0]
                    try:
                        var = int(var[3:-1])
                    except:
                        var = int(var[4:-2])
                else:
                    var = int(j.split(':')[1])

                if var == asn:
                    changesList.append(j.split(':')[2])

    return({y:changesList.count(y) for y in set(changesList)})

def checkReachability(_prefixes):

    prefixes = _prefixes

    totalv4 = 0
    totalv6 = 0

    for i in prefixes:
        i = i.replace(";", "/")
        network = ipaddress.ip_network(i)

        if network.version == 4:
            totalv4 = totalv4 + network.num_addresses
        else:
            totalv6 = totalv6 + network.num_addresses

    return totalv4,totalv6
#------------------------------[PREFIX]-------------------------------------------
#------------------------------[STATISTIC]-------------------------------------------
#count statistics about IXP and ASes and save to a txt file
def countStatistics(_msgList, _ASes, _collectorName):

    totalMSG = 0
    announcement = 0
    withdrawn = 0

    ASes = _ASes
    msglist = _msgList
    collectorName = _collectorName

    for i in ASes:
        msgA,msgW = msgAS(i, msglist)
        prefix,prefixA,prefixW = prefixAS(i, msglist)

        txtAS(i,msgA,msgW,prefix,prefixA,prefixW,collectorName)

        totalMSG = totalMSG + msgA + msgW
        announcement = announcement + msgA
        withdrawn = withdrawn + msgW

    prefix,prefixA,prefixW = prefixIXP(msglist)
    txtIXP(totalMSG,announcement,withdrawn,prefix,prefixA,prefixW,collectorName)

#calculate the time between an announcement and a withdrawn
def calculateTimeAW(_msgList, _prefixes, _label, _prefixSize, _data, _asn):

    prefixes = _prefixes
    msglist = _msgList
    label = _label
    prefixSize = _prefixSize
    data = _data
    asn = _asn

    prefix = {}
    prefixList =[]

    time = 0
    find = 0
    all = 0
    #isAggregate = 0

    if int(prefixSize) == 0:
        all = 1
        path = str(label)+'/reporttimeAW'
        #f = open(str(label)+'/reporttimeWA.txt', 'a+')
    else:
        path = str(label)+'/reporttimeAW-'+str(prefixSize)
        #f = open(str(label)+'/reporttimeWA-'+str(prefixSize)+'.txt', 'a+')

    if int(asn) != 0:
        path = path+'-AS'+str(asn)


    #f = open(path+'.txt', 'a')

    for i in data:
        if(int(i) == int(asn) or int(asn) == 0):
            listA = data[i][0]
            for j in listA:
                find = 0
                #isAggregate = 0
                preA = j["prefix"]
                lprefix = preA.split(";")
                for k in range(0,len(lprefix)-1,2):
                    prefixA = lprefix[k]+';'+lprefix[k+1]
                    test = prefixA.split(";")[1]
                    if (str(prefixSize) == str(test) or int(prefixSize) == 0):
                        listW = data[i][1]
                        if len(listW) == 0:
                            for m in data:
                                if len(data[m][0]) == 0:
                                    listW = data[m][1]
                                    for l in listW:
                                        preW = l["prefix"]
                                        lprefix = preW.split(";")
                                        for n in range(0,len(lprefix)-1,2):
                                            prefixW = lprefix[n]+';'+lprefix[n+1]
                                            test = prefixW.split(";")[1]

                                            test = 0
                                            if (prefixA != prefixW):
                                                test = isAggregate(prefixA,prefixW)
                                                #print(test)

                                            if((prefixA == prefixW or test != 0) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                            #if((prefixA == prefixW or isAggregate(prefixA,prefixW)) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                                dataA = datetime.fromtimestamp(int(j["timestamp"]))
                                                dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                                dataW = datetime.fromtimestamp(int(l["timestamp"]))
                                                dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                                time = dW - dA
                                                find = 1
                                                prefixList.append(i)
                                                listW.remove(l)
                                                #listA.remove(j)
                                                #print(test)
                                                f = open(path+'.txt', 'a')
                                                f.write(str(i)+';'+str(prefixA)+';'+str(time)+';'+str(j["timestamp"])+';'+str(l["timestamp"])+';'+str(j["aspath"])+';'+str(test)+'\n')
                                                f.close()
                        else:
                            for l in listW:
                                preW = l["prefix"]
                                lprefix = preW.split(";")
                                for m in range(0,len(lprefix)-1,2):
                                    prefixW = lprefix[m]+';'+lprefix[m+1]
                                    test = prefixW.split(";")[1]

                                    test = 0
                                    if (prefixA != prefixW):
                                        test = isAggregate(prefixA,prefixW)
                                        #print(test)

                                    if((prefixA == prefixW or test != 0) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                    #if((prefixA == prefixW or isAggregate(prefixA,prefixW)) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                        dataA = datetime.fromtimestamp(int(j["timestamp"]))
                                        dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                        dataW = datetime.fromtimestamp(int(l["timestamp"]))
                                        dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                        time = dW - dA
                                        find = 1
                                        prefixList.append(i)
                                        listW.remove(l)
                                        #listA.remove(j)
                                        #print(test)
                                        f = open(path+'.txt', 'a')
                                        f.write(str(i)+';'+str(prefixA)+';'+str(time)+';'+str(j["timestamp"])+';'+str(l["timestamp"])+';'+str(j["aspath"])+';'+str(test)+'\n')
                                        f.close()

    #for i in prefixes:
    #    if (i.split(';')[1] == prefixSize or all == 1):
    #        for j in msglist:
    #            find = 0
    #            if i == j["prefix"] and j["type"] == 'a':
    #                for k in msglist:
    #                    if k["type"] == 'w' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
    #                        list = k["prefix"].split(';')
    #                        for l in range(0,len(list)-1,2):
    #                            if i == list[l]+';'+list[l+1]:
    #                                dataA = datetime.fromtimestamp(int(j["timestamp"]))
    #                                dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
    #                                dataW = datetime.fromtimestamp(int(k["timestamp"]))
    #                                dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
    #                                time = dW - dA
    #                                find = 1
    #                                prefixList.append(i)
    #                                msglist.remove(j)
    #                                msglist.remove(k)
    #                                f.write(str(time)+'\n')

    #f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#calculate the time between an withdrawn and a announcement
def calculateTimeWA(_msgList, _prefixes, _label, _prefixSize, _data, _asn):

    prefixes = _prefixes
    msglist = _msgList
    label = _label
    prefixSize = _prefixSize
    data = _data
    asn = _asn

    prefix = {}
    prefixList =[]

    time = 0
    find = 0
    all = 0
    #isAggregate = 0

    if int(prefixSize) == 0:
        all = 1
        path = str(label)+'/reporttimeWA'
        #f = open(str(label)+'/reporttimeWA.txt', 'a+')
    else:
        path = str(label)+'/reporttimeWA-'+str(prefixSize)
        #f = open(str(label)+'/reporttimeWA-'+str(prefixSize)+'.txt', 'a+')

    if int(asn) != 0:
        path = path+'-AS'+str(asn)


    #f = open(path+'.txt', 'a')

    for i in data:
        if(int(i) == int(asn) or int(asn) == 0):
            listW = data[i][1]
            for j in listW:
                find = 0
                #isAggregate = 0
                preW = j["prefix"]
                lprefix = preW.split(";")
                for k in range(0,len(lprefix)-1,2):
                    prefixW = lprefix[k]+';'+lprefix[k+1]
                    test = prefixW.split(";")[1]
                    if (str(prefixSize) == str(test) or int(prefixSize) == 0):
                        listA = data[i][0]
                        if len(listA) == 0:
                            for m in data:
                                if len(data[m][1]) == 0:
                                    listA = data[m][0]
                                    for l in listA:
                                        prefixA = l["prefix"]

                                        test = 0
                                        if (prefixA != prefixW):
                                            test = isAggregate(prefixA,prefixW)
                                            #print(test)

                                        if((prefixA == prefixW or test != 0) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                        #if((prefixA == prefixW or isAggregate(prefixA,prefixW)) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                            dataW = datetime.fromtimestamp(int(j["timestamp"]))
                                            dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                            dataA = datetime.fromtimestamp(int(l["timestamp"]))
                                            dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                            time = dA - dW
                                            find = 1
                                            prefixList.append(i)
                                            #listW.remove(j)
                                            listA.remove(l)

                                            #print(test)
                                            f = open(path+'.txt', 'a')
                                            f.write(str(i)+';'+str(prefixW)+';'+str(time)+';'+str(j["timestamp"])+';'+str(l["timestamp"])+';'+str(l["aspath"])+';'+str(test)+'\n')
                                            f.close()
                        else:
                            for l in listA:
                                prefixA = l["prefix"]

                                if (prefixA != prefixW):
                                    test = isAggregate(prefixA,prefixW)
                                    #print(test)

                                if((prefixA == prefixW or test != 0) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                #if((prefixA == prefixW or isAggregate(prefixA,prefixW)) and find == 0 and int(l["timestamp"]) >= int(j["timestamp"])):
                                    dataW = datetime.fromtimestamp(int(j["timestamp"]))
                                    dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                    dataA = datetime.fromtimestamp(int(l["timestamp"]))
                                    dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                    time = dA - dW
                                    find = 1
                                    prefixList.append(i)
                                    #listW.remove(j)
                                    listA.remove(l)
                                    #print(test)
                                    f = open(path+'.txt', 'a')
                                    f.write(str(i)+';'+str(prefixW)+';'+str(time)+';'+str(j["timestamp"])+';'+str(l["timestamp"])+';'+str(l["aspath"])+';'+str(test)+'\n')
                                    f.close()
    #for i in prefixes:
    #    if (i.split(';')[1] == prefixSize or all == 1):
    #        for j in msglist:
    #            find = 0
    #            if j["type"] == 'w':
    #                list = j["prefix"].split(';')
    #                for l in range(0,len(list)-1,2):
    #                    if i == list[l]+';'+list[l+1]:
    #                        for k in msglist:
    #                            if i == k["prefix"] and k["type"] == 'a' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
    #                                dataW = datetime.fromtimestamp(int(j["timestamp"]))
    #                                dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
    #                                dataA = datetime.fromtimestamp(int(k["timestamp"]))
    #                                dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
    #                                time = dA - dW
    #                                find = 1
    #                                prefixList.append(i)
    #                                msglist.remove(j)
    #                                msglist.remove(k)
    #                                f.write(str(time)+'\n')
    #f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#TODO fix
def calculateTimeA(_msgList, _prefixes, _label):

    prefixes = _prefixes
    msglist = _msgList
    label = _label

    prefix = {}
    prefixList =[]

    time = 0
    find = 0

    for i in prefixes:
        for j in msglist:
            find = 0
            if i == j["prefix"] and j["type"] == 'a':
                for k in msglist:
                    if k["type"] == 'w' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
                        list = k["prefix"].split(';')
                        for l in range(0,len(list)-1,2):
                            if i == list[l]+';'+list[l+1]:
                                find = 1
                                msglist.remove(j)
                                msglist.remove(k)
                if find == 0:
                    dataA = datetime.fromtimestamp(int(j["timestamp"]))
                    dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                    dataW = datetime.fromtimestamp(int(msglist[-1]["timestamp"]))
                    dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                    time = dW - dA
                    prefixList.append(i)
                    f = open('reports/timeA'+label+'.txt', 'a+')
                    f.write(str(time)+'\n')
                    f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#TODO fix
def calculateTimeW(_msgList, _prefixes, _label):

    prefixes = _prefixes
    msglist = _msgList
    label = _label

    prefix = {}
    prefixList =[]

    time = 0
    find = 0

    for i in prefixes:
        for j in msglist:
            find = 0
            if j["type"] == 'w':
                list = j["prefix"].split(';')
                for l in range(0,len(list)-1,2):
                    if i == list[l]+';'+list[l+1]:
                        for k in msglist:
                            if i == k["prefix"] and k["type"] == 'a' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
                                find == 1
                                #msglist.remove(j)
                                #msglist.remove(k)
                        if find == 0:
                            dataW = datetime.fromtimestamp(int(j["timestamp"]))
                            dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                            dataA = datetime.fromtimestamp(int(msglist[-1]["timestamp"]))
                            dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                            time = dA - dW
                            prefixList.append(i)
                            f = open('reports/timeW'+label+'.txt', 'a+')
                            f.write(str(time)+'\n')
                            f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#TODO fix
#calculate how many changes and how many ases announced each prefix
def calculateChangesPrefix(_prefixes, _msglist, _label):

    prefixes = _prefixes
    msglist = _msglist
    label = _label
    for i in prefixes:
        var1,var2 = prefixChanges(i, prefixes, msglist)
        txtPrefix(i,len(var1),len(var2), label)

#calculate how many changes every tuple(as,prefix) have
def calculateChangesASPrefix(_prefixes, _ases, _msglist, _label):

    prefixes = _prefixes
    msglist = _msglist
    label = _label
    ases = _ases

    for i in prefixes:
        for j in ases:
            var1 = prefixASChanges(i, j, prefixes, msglist)
            if len(var1) != 0:
                txtPrefix2(i,j,len(var1),label)

#TODO
#calculate how many changes every tuple(as,prefix) have
def calculateChangesASPrefix_new(_prefixes, _ases, _data, _label):

    prefixes = _prefixes
    data = _data
    label = _label
    ases = _ases

    for i in prefixes:
        for j in ases:
            var1 = prefixASChanges(i, j, prefixes, msglist)
            if len(var1) != 0:
                txtPrefix2(i,j,len(var1),label)

#find the cases inside the threshold
def findPrefixThreshold(_label, _path, _threshold, _type):

    label = _label
    path = _path
    threshold = _threshold
    type = _type
    path = path+".txt"
    if type == 0:
        typepath = "AW"
    else:
        typepath = "WA"
    f = open(label+'/reportPrefixThreshold-'+str(threshold)+typepath+'-NEW.txt', 'a+')

    with open(path) as fp:
        line = fp.readline()
        while line:
            nAs = line.split(";")[0]
            prefix = line.split(";")[1]+"/"+line.split(";")[2]
            aux = line.split(";")[3]
            try:
                days = aux.split(",")[0]
                days = int(days[:1])
                hours = aux.split(",")[1]
                h = int(hours.split(":")[0])
                m = int(hours.split(":")[1])
                s = int(hours.split(":")[2])
                time = s/60 + m + h*60 + days*24
            except:
                h = int(aux.split(":")[0])
                m = int(aux.split(":")[1])
                s = int(aux.split(":")[2])
                time = s/60 + m + h*60
            #print (time)
            if (time < threshold):
                f.write(str(prefix)+'\n')
            line = fp.readline()

    f.close()

#read file of report and count wich prefix apear and how much time
def wichPrefixHasChanged(_path):

    path = _path
    prefixList = []

    with open(path) as fp:
        line = fp.readline()
        while line:
            prefix = line.split(';')[1] + '/' + line.split(';')[2]
            prefixList.append(prefix)
            line = fp.readline()

    prefixes = {x:prefixList.count(x) for x in set(prefixList)}
    #print(len(prefixes))

    return prefixes, len(prefixes)

#calculate the average time for each prefix
def averageTimeByPrefix(_path, _prefix):

    path = _path
    timeList = []
    prefix = _prefix
    averageTime = 0

    with open(path) as fp:
        line = fp.readline()
        while line:
            if prefix == line.split(';')[1] +'/'+ line.split(';')[2]:
                time = line.split(';')[3]
                try:
                    day = time.split(',')[0]
                    day = int(day[:1])
                    rest = time.split(',')[1]
                    hour = int(rest.split(':')[0])
                    min = int(rest.split(':')[1])
                    sec = int(rest.split(':')[2])
                    total = sec/60 + min + hour*60 + day*24*60
                    timeList.append(total)
                    line = fp.readline()

                except:
                    hour = int(time.split(":")[0])
                    min = int(time.split(":")[1])
                    sec = int(time.split(":")[2])
                    total = sec/60 + min + hour*60
                    timeList.append(total)
                    line = fp.readline()
            else:
                line = fp.readline()

    for i in timeList:
        averageTime = averageTime + i

    if len(timeList) != 0:
        averageTime = averageTime/len(timeList)

    #print(averageTime)

    return averageTime

#return the most repeated prefix of IPv4 or IPv6
def mostRepeatedPrefix(_path, _version):

    path = _path
    version = int(_version)

    prefix = {}
    prefixList =[]

    with open(path) as fp:
        line = fp.readline()
        while line:
            prefix = line.split('\n')[0]
            if ipaddress.ip_network(prefix).version == version:
                prefixList.append(prefix)
            line = fp.readline()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    print(prefix)

    print(max(set(prefixList), key=prefixList.count))

    return(max(set(prefixList), key=prefixList.count))

#TODO: menu
#calculate the average time by each prefix
def calculateAverageTimebyPrefix(_path):
    path = _path
    save = path.split('/')[0]

    f = open(save+'/reportPrefixesWA.txt', 'a+')
    f.write('\n'+'LINIX_'+'\n')
    a,b = wichPrefixHasChanged(path)
    f.write('Number of prefixes: '+str(b)+'\n')
    f.write('averageTimes'+'\n')
    for i in a:
        c = averageTimeByPrefix(path,i)
        f.write(i+': '+str(c)+'\n')
    f.close()

#list the prefixes with the highest times
def highestTimes(_path):

    path = _path

    tamanho = 0
    listtimes = []

    print(path)
    with open(path) as fp:
        line = fp.readline()
        line = fp.readline()
        tamanho = line.split(': ')[1]
        line = fp.readline()
        line = fp.readline()
        while line:
            listtimes.append(float(line.split(': ')[1]))
            line = fp.readline()
    print('tamanho')
    print(tamanho)
    print('média')
    print(sum(listtimes)/len(listtimes))
    listtimes.sort()

    print(listtimes[len(listtimes)-1])
    print(listtimes[len(listtimes)-2])
    print(listtimes[len(listtimes)-3])
    print(listtimes[len(listtimes)-4])
    print(listtimes[len(listtimes)-5])

def diffTable():

    listPrefix1 = []
    listPrefix2 = []
    listPrefix3 = []
    listPrefix4 = []

    with open('LINIX_010119_070119_new/reportPrefixesAW.txt') as fp:
        line = fp.readline()
        line = fp.readline()
        tamanho = line.split(': ')[1]
        line = fp.readline()
        line = fp.readline()
        while line:
            listPrefix1.append(line.split(':')[0])
            line = fp.readline()

    with open('LINIX_080119_140119_new/reportPrefixesAW.txt') as fp:
        line = fp.readline()
        line = fp.readline()
        tamanho = line.split(': ')[1]
        line = fp.readline()
        line = fp.readline()
        while line:
            listPrefix2.append(line.split(':')[0])
            line = fp.readline()

    with open('LINIX_150119_210119_new/reportPrefixesAW.txt') as fp:
        line = fp.readline()
        line = fp.readline()
        tamanho = line.split(': ')[1]
        line = fp.readline()
        line = fp.readline()
        while line:
            listPrefix3.append(line.split(':')[0])
            line = fp.readline()

    with open('LINIX_220119_280119_new/reportPrefixesAW.txt') as fp:
        line = fp.readline()
        line = fp.readline()
        tamanho = line.split(': ')[1]
        line = fp.readline()
        line = fp.readline()
        while line:
            listPrefix4.append(line.split(':')[0])
            line = fp.readline()

    one_two = len(set(listPrefix1) - set(listPrefix2))
    one_three = len(set(listPrefix1) - set(listPrefix3))
    one_four = len(set(listPrefix1) - set(listPrefix4))
    one = len(set(listPrefix1) - set(listPrefix2) - set(listPrefix3) - set(listPrefix4))

    two_one = len(set(listPrefix2) - set(listPrefix1))
    two_three = len(set(listPrefix2) - set(listPrefix3))
    two_four = len(set(listPrefix2) - set(listPrefix4))
    two = len(set(listPrefix2) - set(listPrefix1) - set(listPrefix3) - set(listPrefix4))

    three_one = len(set(listPrefix3) - set(listPrefix1))
    three_two = len(set(listPrefix3) - set(listPrefix2))
    three_four = len(set(listPrefix3) - set(listPrefix4))
    three = len(set(listPrefix3) - set(listPrefix1) - set(listPrefix2) - set(listPrefix4))

    four_one = len(set(listPrefix4) - set(listPrefix1))
    four_two = len(set(listPrefix4) - set(listPrefix2))
    four_three = len(set(listPrefix4) - set(listPrefix3))
    four = len(set(listPrefix4) - set(listPrefix1) - set(listPrefix2) - set(listPrefix3))

    print(one_two)
    print(one_three)
    print(one_four)
    print(one)

    print(two_one)
    print(two_three)
    print(two_four)
    print(two)

    print(three_one)
    print(three_two)
    print(three_four)
    print(three)

    print(four_one)
    print(four_two)
    print(four_three)
    print(four)
#------------------------------[STATISTIC]-------------------------------------------
#------------------------------[PLOT]------------------------------------------------
#plot information about the IXP
def plotIXPmsg():

    d1 = []
    d2 = []
    d3 = []
    d4 = []

    path1 = "DECIX_010119_070119_new/reportIXP.txt"
    path2 = "DECIX_080119_140119/reportIXP.txt"
    path3 = "DECIX_150119_210119/reportIXP.txt"
    path4 = "DECIX_220119_280119/reportIXP.txt"

    with open(path1) as fp1:
        line = fp1.readline()
        d1.append(int(line.split(";")[0]))
        d1.append(int(line.split(";")[1]))
        d1.append(int(line.split(";")[2]))

    with open(path2) as fp2:
        line = fp2.readline()
        d2.append(int(line.split(";")[0]))
        d2.append(int(line.split(";")[1]))
        d2.append(int(line.split(";")[2]))

    with open(path3) as fp3:
        line = fp3.readline()
        d3.append(int(line.split(";")[0]))
        d3.append(int(line.split(";")[1]))
        d3.append(int(line.split(";")[2]))

    with open(path4) as fp4:
        line = fp4.readline()
        d4.append(int(line.split(";")[0]))
        d4.append(int(line.split(";")[1]))
        d4.append(int(line.split(";")[2]))

    ind = np.arange(len(d1))  # the x locations for the groups
    width = 0.12  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 3/2*width, d1, width, color='SkyBlue', label='010119-070119')
    rects2 = ax.bar(ind - 1/2*width, d2, width, color='IndianRed', label='080119-140119')
    rects3 = ax.bar(ind + 1/2*width, d3, width, color='Chocolate', label='150119-210119')
    rects4 = ax.bar(ind + 3/2*width, d4, width, color='Orange', label='220119-280119')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of')
    ax.set_title('BGP Messages')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total Messages', 'Announcement Messages', 'Withdrawn Messages'))
    ax.legend()

    def autolabel(rects, xpos='center'):
        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                    '{}'.format(height), ha=ha[xpos], va='bottom')

    autolabel(rects1, "left")
    autolabel(rects2, "center")
    autolabel(rects3, "center")
    autolabel(rects4, "right")

    plt.show()
    plt.savefig("IXPmsg.pdf", dpi=600)
    plt.savefig("IXPmsg.png", dpi=600)
    plt.clf()

#plot information about the IXP
def plotIXPprefix():

    d1 = []
    d2 = []
    d3 = []
    d4 = []

    path1 = "DECIX_010119_070119_new/reportIXP.txt"
    path2 = "DECIX_080119_140119/reportIXP.txt"
    path3 = "DECIX_150119_210119/reportIXP.txt"
    path4 = "DECIX_220119_280119/reportIXP.txt"

    with open(path1) as fp1:
        line = fp1.readline()
        d1.append(int(line.split(";")[3]))
        d1.append(int(line.split(";")[4]))
        d1.append(int(line.split(";")[5]))

    with open(path2) as fp2:
        line = fp2.readline()
        d2.append(int(line.split(";")[3]))
        d2.append(int(line.split(";")[4]))
        d2.append(int(line.split(";")[5]))

    with open(path3) as fp3:
        line = fp3.readline()
        d3.append(int(line.split(";")[3]))
        d3.append(int(line.split(";")[4]))
        d3.append(int(line.split(";")[5]))

    with open(path4) as fp4:
        line = fp4.readline()
        d4.append(int(line.split(";")[3]))
        d4.append(int(line.split(";")[4]))
        d4.append(int(line.split(";")[5]))

    ind = np.arange(len(d1))  # the x locations for the groups
    width = 0.12  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 3/2*width, d1, width, color='SkyBlue', label='010119-070119')
    rects2 = ax.bar(ind - 1/2*width, d2, width, color='IndianRed', label='080119-140119')
    rects3 = ax.bar(ind + 1/2*width, d3, width, color='Chocolate', label='150119-210119')
    rects4 = ax.bar(ind + 3/2*width, d4, width, color='Orange', label='220119-280119')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of')
    ax.set_title('BGP Prefixes' )
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total Prefixes', 'Prefixes Announced ', 'Prefixes Withdrawals'))
    ax.legend()

    def autolabel(rects, xpos='center'):
        xpos = xpos.lower()  # normalize the case of the parameter
        ha = {'center': 'center', 'right': 'left', 'left': 'right'}
        offset = {'center': 0.5, 'right': 0.57, 'left': 0.43}  # x_txt = x + w*off
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()*offset[xpos], 1.01*height,
                    '{}'.format(height), ha=ha[xpos], va='bottom')

    autolabel(rects1, "center")
    autolabel(rects2, "center")
    autolabel(rects3, "center")
    autolabel(rects4, "center")


    plt.show()
    plt.savefig("IXPprefix_new.pdf", dpi=600)
    plt.savefig("IXPprefix_new.png", dpi=600)
    plt.clf()

#plot times between messages AW and WA
def plotCDF(_type, _threshold, _as, _prefix):

    type = _type
    threshold = _threshold
    nAs = _as
    prefix = int(_prefix)
    count = 0
    timeList1 = []
    timeList2 = []
    timeList3 = []
    timeList4 = []

    path1 = "AMSIX_010119_070119_new/reporttime"+type+".txt"
    path2 = "AMSIX_080119_140119/reporttime"+type+".txt"
    path3 = "AMSIX_150119_210119/reporttime"+type+".txt"
    path4 = "AMSIX_220119_280119/reporttime"+type+".txt"

    if type == "WA":
        name = "a Withdrawn and an Announcement"
        save = "timeWA"
    else:
        name = "an Announcement and a Withdrawn"
        save = "timeAW"

    if(threshold != 0):
        save = save+"-"+str(threshold)

    if(nAs != 0):
        save = save+"-AS"+str(nAs)

    if(prefix != 0):
        save = save+"-prefix"+str(prefix)

    with open(path1) as fp1:
        days = 0
        readAS = 0
        readPrefix = ''
        readTime = ''
        line = fp1.readline()
        while line:
            readAS = int(line.split(';')[0])
            readPrefix = int(line.split(';')[2])
            readTime = line.split(';')[3]
            try:
                days = readTime.split(",")[0]
                days = int(days[:1])
                hours = readTime.split(",")[1]
                h = int(hours.split(":")[0])
                m = int(hours.split(":")[1])
                s = int(hours.split(":")[2])
                time = s/60 + m + h*60 + days*24*60
                if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                    timeList1.append(time)
                line = fp1.readline()
            except:
                h = int(readTime.split(":")[0])
                m = int(readTime.split(":")[1])
                s = int(readTime.split(":")[2])
                time = s/60 + m + h*60
                if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                    timeList1.append(time)
                line = fp1.readline()

    with open(path2) as fp2:
            days = 0
            readAS = 0
            readPrefix = ''
            readTime = ''
            line = fp2.readline()
            while line:
                readAS = int(line.split(';')[0])
                readPrefix = int(line.split(';')[2])
                readTime = line.split(';')[3]
                try:
                    days = readTime.split(",")[0]
                    days = int(days[:1])
                    hours = readTime.split(",")[1]
                    h = int(hours.split(":")[0])
                    m = int(hours.split(":")[1])
                    s = int(hours.split(":")[2])
                    time = s/60 + m + h*60 + days*24*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList2.append(time)
                    line = fp2.readline()
                except:
                    h = int(readTime.split(":")[0])
                    m = int(readTime.split(":")[1])
                    s = int(readTime.split(":")[2])
                    time = s/60 + m + h*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList2.append(time)
                    line = fp2.readline()

    with open(path3) as fp3:
            days = 0
            readAS = 0
            readPrefix = ''
            readTime = ''
            line = fp3.readline()
            while line:
                readAS = int(line.split(';')[0])
                readPrefix = int(line.split(';')[2])
                readTime = line.split(';')[3]
                try:
                    days = readTime.split(",")[0]
                    days = int(days[:1])
                    hours = readTime.split(",")[1]
                    h = int(hours.split(":")[0])
                    m = int(hours.split(":")[1])
                    s = int(hours.split(":")[2])
                    time = s/60 + m + h*60 + days*24*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList3.append(time)
                    line = fp3.readline()
                except:
                    h = int(readTime.split(":")[0])
                    m = int(readTime.split(":")[1])
                    s = int(readTime.split(":")[2])
                    time = s/60 + m + h*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList3.append(time)
                    line = fp3.readline()

    with open(path4) as fp4:
            days = 0
            readAS = 0
            readPrefix = ''
            readTime = ''
            line = fp4.readline()
            while line:
                readAS = int(line.split(';')[0])
                readPrefix = int(line.split(';')[2])
                readTime = line.split(';')[3]
                try:
                    days = readTime.split(",")[0]
                    days = int(days[:1])
                    hours = readTime.split(",")[1]
                    h = int(hours.split(":")[0])
                    m = int(hours.split(":")[1])
                    s = int(hours.split(":")[2])
                    time = s/60 + m + h*60 + days*24*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList4.append(time)
                    line = fp4.readline()
                except:
                    h = int(readTime.split(":")[0])
                    m = int(readTime.split(":")[1])
                    s = int(readTime.split(":")[2])
                    time = s/60 + m + h*60
                    if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == '')):
                        timeList4.append(time)
                    line = fp4.readline()

    pylab.plot(np.sort(timeList1),np.arange(len(timeList1))/float(len(timeList1)-1), color='SkyBlue', label="010119-070119 - "+ str(len(timeList1)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(timeList2),np.arange(len(timeList2))/float(len(timeList2)-1), color='IndianRed', label="080119-140119 - "+ str(len(timeList2)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(timeList3),np.arange(len(timeList3))/float(len(timeList3)-1), color='Chocolate', label="150119-210119 - "+ str(len(timeList3)),  linewidth=2, linestyle='-.')
    pylab.plot(np.sort(timeList4),np.arange(len(timeList4))/float(len(timeList4)-1), color='Orange', label="220119-280119 - "+ str(len(timeList4)),  linewidth=2, linestyle=':')
    pylab.title("Time between " + name, loc='center')
    pylab.ylabel("Frequency", fontsize=10)
    pylab.xlabel("Time (min)", fontsize=10)
    pylab.grid(True)
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=10)
    pylab.savefig("AMSIX_newplots/"+save+".pdf", dpi=600)
    pylab.savefig("AMSIX_newplots/"+save+".png", dpi=600)
    pylab.clf()

#plot number of changes in aspath
def plotCDFASPrefix():

    path1 = "AMSIX_080418_140418/reportprefixesASes.txt"
    path2 = "AMSIX_010119_070119/reportprefixesASes.txt"
    path3 = "DECIX_080418_140418/reportprefixesASes.txt"
    path4 = "DECIX_010119_070119/reportprefixesASes.txt"

    changesList1 = []
    changesList2 = []
    changesList3 = []
    changesList4 = []
    count = 0

    save = "prefixesASes"

    with open(path1) as fp:
        line = fp.readline()
        while line:
            num = int(line.split(";")[3])
            changesList1.append(num)
            line = fp.readline()

    with open(path2) as fp2:
        line = fp2.readline()
        while line:
            num = int(line.split(";")[3])
            changesList2.append(num)
            line = fp2.readline()

    with open(path3) as fp3:
        line = fp3.readline()
        while line:
            num = int(line.split(";")[3])
            changesList3.append(num)
            line = fp3.readline()

    with open(path4) as fp4:
        line = fp4.readline()
        while line:
            num = int(line.split(";")[3])
            changesList4.append(num)
            line = fp4.readline()

    pylab.plot(np.sort(changesList1),np.arange(len(changesList1))/float(len(changesList1)-1), color='SkyBlue', label='AMSIX_080418_140418 - ' + str(len(changesList1)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(changesList2),np.arange(len(changesList2))/float(len(changesList2)-1), color='IndianRed', label='AMSIX_010119_070119 - ' + str(len(changesList2)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(changesList3),np.arange(len(changesList3))/float(len(changesList3)-1), color='Chocolate', label='DECIX_080418_140418 - ' + str(len(changesList3)),  linewidth=2, linestyle='-.')
    pylab.plot(np.sort(changesList4),np.arange(len(changesList4))/float(len(changesList4)-1), color='Orange', label='DECIX_010119_070119 - ' + str(len(changesList4)),  linewidth=2, linestyle=':')
    pylab.title("(Prefix,AS) - ASPATH Changes", loc='center')
    pylab.ylabel("Frequency", fontsize=10)
    pylab.xlabel("Number of changes", fontsize=10)
    pylab.grid(True)
    plt.xticks(np.arange(min(changesList2), max(changesList2)+1, 1.0))
    pylab.xlim(0, 20)
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=12)
    pylab.savefig(save+".pdf", dpi=600)
    pylab.savefig(save+".png", dpi=600)
    pylab.clf()

#plot number of changes in aspath
def plotCDFShortLivedEvent(_type, _threshold, _as, _prefix):

    type = _type
    threshold = _threshold
    nAs = _as
    prefix = int(_prefix)
    count = 0

    path1 = "AMSIX_010119_070119_new/reporttime"+type+".txt"
    print(path1)
    changesList1 = []
    changesList2 = []
    changesList3 = []
    #changesList4 = []
    count = 0

    if type == "WA":
        save = "ShortLivedEvent-WA"
    else:
        save = "ShortLivedEvent-AW"

    if(threshold != 0):
        save = save+"-"+str(threshold)

    if(nAs != 0):
        save = save+"-AS"+str(nAs)

    if(prefix != 0):
        save = save+"-prefix"+str(prefix)

    with open(path1) as fp:
        days = 0
        readAS = 0
        readPrefix = ''
        readTime = ''
        line = fp.readline()
        while line:
            print(line)
            readAS = int(line.split(';')[0])
            readPrefix = int(line.split(';')[2])
            readTime = line.split(';')[3]
            aux = int(line.split(";")[7])
            #print(aux)
            try:
                days = readTime.split(",")[0]
                days = int(days[:1])
                hours = readTime.split(",")[1]
                h = int(hours.split(":")[0])
                m = int(hours.split(":")[1])
                s = int(hours.split(":")[2])
                time = s/60 + m + h*60 + days*24*60
                print(time)
                print('time')
                if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == 0)):
                    if aux == 0:
                        print('entrou0')
                        changesList1.append(time)
                    if aux == 1:
                        print('entrou1')
                        changesList2.append(time)
                    if aux == 2:
                        print('entrou2')
                        changesList3.append(time)
                line = fp.readline()
            except:
                h = int(readTime.split(":")[0])
                m = int(readTime.split(":")[1])
                s = int(readTime.split(":")[2])
                time = s/60 + m + h*60
                print(time)
                print('time')
                if (time > threshold and (nAs == readAS or nAs == 0) and (prefix == readPrefix or prefix == 0)):
                    if aux == 0:
                        print('entrou0')
                        changesList1.append(time)
                    if aux == 1:
                        print('entrou1')
                        changesList2.append(time)
                    if aux == 2:
                        print('entrou2')
                        changesList3.append(time)
                line = fp.readline()
        line = fp.readline()


    print(len(changesList1))
    print(len(changesList2))
    print(len(changesList3))

    pylab.plot(np.sort(changesList1),np.arange(len(changesList1))/float(len(changesList1)-1), color='SkyBlue', label='exact match - ' + str(len(changesList1)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(changesList2),np.arange(len(changesList2))/float(len(changesList2)-1), color='IndianRed', label='disaggregation - ' + str(len(changesList2)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(changesList3),np.arange(len(changesList3))/float(len(changesList3)-1), color='Chocolate', label='aggregation - ' + str(len(changesList3)),  linewidth=2, linestyle='-.')
    #pylab.plot(np.sort(changesList4),np.arange(len(changesList4))/float(len(changesList4)-1), color='Orange', label='DECIX_010119_070119 - ' + str(len(changesList4)),  linewidth=2, linestyle=':')
    pylab.title("Test Plot", loc='center')
    pylab.ylabel("Frequency", fontsize=10)
    pylab.xlabel("Time (min)", fontsize=10)
    pylab.grid(True)
    #plt.xticks(np.arange(min(changesList2), max(changesList2)+1, 1.0))
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=12)
    plt.show()
    #pylab.savefig(save+".pdf", dpi=600)
    #pylab.savefig(save+".png", dpi=600)
    pylab.clf()


#TODO fix
#plot ASes information
def printASes(_listASNs, _date):

    listASNs = _listASNs
    date = _date
    numA = []
    numW = []
    listASs = []

    for i in listASNs:
        with open("reports/AMSIX/AS"+str(i)+".txt") as fp:
            line = fp.readline()
            while line:
                if(line.split(";")[0] == date):
                    a = int(line.split(";")[5])
                    w = int(line.split(";")[6])
                    listASs.append(str(i))
                    numA.append(a)
                    numW.append(w)
                line = fp.readline()

    N = len(listASNs)
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, numA, width)
    p2 = plt.bar(ind, numW, width, bottom=numA)

    plt.ylabel('Number of Prefixes')
    plt.title('Prefixes of ASes - ' + date )
    plt.semilogy(ind, np.exp(-ind/5.0))
    plt.xticks(ind, listASs, fontsize=8)
    plt.legend((p1[0], p2[0]), ('Announced', 'Withdrawed'))
    plt.savefig("figures/amsixASes"+date+".pdf", dpi=600)
    plt.savefig("figures/amsixASes"+date+".png", dpi=600)
    plt.show()
    plt.clf()

#plot time series of life and death of a prefix
def plotLifeTime(_path, _prefix, _startTimestamp, _stopTimestamp):

    path = _path
    prefix = _prefix
    startTimestamp = _startTimestamp
    stopTimestamp = _stopTimestamp
    names = []
    dates = []
    print(prefix)
    save = path.split('/')[0]
    #prefix = '104.237.191.0/24'

    #with open("AMSIX_010119_070119_new2/reporttimeAW-AS15169.txt") as fp:
    with open(path) as fp:
        line = fp.readline()
        while line:
            if prefix == line.split(';')[1] + '/' + line.split(';')[2]:
                dates.append(line.split(';')[4])
                names.append("A")
                dates.append(line.split(';')[5])
                names.append("W")
            line = fp.readline()

    dates = [datetime.fromtimestamp(int(ii)) for ii in dates]
    #dates = [datetime.strptime(((datetime.fromtimestamp(1546300809)).strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S') for ii in dates]

    levels = np.array([-1, 1])
    fig, ax = plt.subplots(figsize=(15, 5))

    #start = min(dates)
    start = datetime.fromtimestamp(startTimestamp)
    #stop = max(dates)
    stop = datetime.fromtimestamp(stopTimestamp)

    ax.plot((start, stop), (0, 0), 'k', alpha=.5)

    for ii, (iname, idate) in enumerate(zip(names, dates)):
        level = levels[ii % 2]
        vert = 'top' if level < 0 else 'bottom'

        ax.scatter(idate, 0, s=100, facecolor='w', edgecolor='k', zorder=9999)
        if vert == 'top':
            ax.plot((idate, idate), (0, level), c='b', alpha=.7)
        else:
            ax.plot((idate, idate), (0, level), c='r', alpha=.7)
        ax.text(idate, level, iname,
                horizontalalignment='right', verticalalignment=vert, fontsize=10,
                backgroundcolor=(1., 1., 1., .3))
    ax.set(title="PREFIX LIFETIME - " + prefix)

    ax.get_xaxis().set_major_locator(mdates.HourLocator(interval=6))
    ax.get_xaxis().set_major_formatter(mdates.DateFormatter("%d/%m/%Y - %H:%M"))
    fig.autofmt_xdate()

    plt.setp((ax.get_yticklabels() + ax.get_yticklines() + list(ax.spines.values())), visible=False)
    plt.show()
    prefix = prefix.replace('/',';')
    #plt.savefig(save+"/lifetime-"+prefix+".pdf", dpi=600)
    #plt.savefig(save+"/lifetime-"+prefix+".png", dpi=600)
    plt.clf()

#plot time series of life and death of each prefix
def plotLifeTimeforEveryprefix(_nAS, _path, _timestamp1, _timestamp2):

    nAS = _nAS
    path = _path
    timestamp1 = _timestamp1
    timestamp2 = _timestamp2

    prefixes,b = wichPrefixHasChanged(path)
    if len(prefixes) != 0:
        for j in prefixes:
            plotLifeTime(path, j,timestamp1,timestamp2)
#------------------------------[PLOT]---------------------------------------------

def cli():
    help()
    while True:
        action = input("BGPstability: ")
        if len(action) > 0:
                if "TXTtoMem" in action:
                    announcement = 0
                    withdrawn = 0
                    msglist = []
                    aux = action.split("TXTtoMem(")[1]
                    aux = aux[:-1]
                    aux = aux.split(",")
                    collectorName = aux[0]
                    #numberDays = aux[1]
                    path = aux[1]
                    if not os.path.exists(collectorName):
                        os.makedirs(collectorName)

                    auxlist,ases,prefix,data = txttoMemory_new(path,collectorName)
                    dataAW = copy.deepcopy(data)
                    dataWA = copy.deepcopy(data)

                    #print(data)

                    for i in data:
                        announcement = len(data[i][0]) + announcement
                        withdrawn = len(data[i][1]) + withdrawn

                    print("announcements:")
                    print(announcement)
                    print("Withdrawals:")
                    print(withdrawn)

                    txtIXP(announcement+withdrawn,announcement,withdrawn,0,0,0,collectorName)

                    ASes = {x:ases.count(x) for x in set(ases)}
                    txtIXP2(ASes,collectorName)
                    prefixes = {x:prefix.count(x) for x in set(prefix)}
                    #print(prefixes)

                    numberv4, numberv6 = checkReachability(prefixes)
                    print("num IPv4:")
                    print(numberv4)
                    print("num IPv6:")
                    print(numberv6)

                    #TODO: check path changes

                    #print("Looking for which ASes sent messages","\n")
                    #ASes = countASes(msglist)

                    #print('Looking for which prefix',"\n")
                    #prefixes = countPrefix(msglist)

                elif "Count Statistics" in action:
                    print('Counting statistics and saving to a txt file',"\n")
                    countStatistics(msglist,ASes,collectorName)

                elif "CalculateAW" in action:
                    aux = action.split("CalculateAW(")[1]
                    aux = aux[:-1]
                    prefixSize,asn=aux.split(',')
                    print('Calculating the time between an announcement and a withdrawn',"\n")
                    calculateTimeAW(msglist, prefixes, collectorName, prefixSize, dataAW, asn)

                elif "CalculateWA" in action:
                    aux = action.split("CalculateWA(")[1]
                    aux = aux[:-1]
                    prefixSize,asn=aux.split(',')
                    print('Calculating the time between a withdrawn and an announcement',"\n")
                    calculateTimeWA(msglist, prefixes, collectorName, prefixSize, dataWA, asn)

                elif "CalculateChangesASPrefix" in action:
                    prefixSize = action.split("CalculateChangesASPrefix(")[1]
                    prefixSize = prefixSize[:-1]
                    print('Calculating the changes of each (prefix,AS)',"\n")
                    calculateChangesASPrefix(prefixes,ASes,msglist, collectorName)

                elif "CalculateALL" in action:
                    aux = action.split("CalculateALL(")[1]
                    aux = aux[:-1]
                    prefixSize,asn=aux.split(',')
                    print('Calculating the changes of each (prefix,AS)',"\n")
                    calculateTimeWA(msglist, prefixes, collectorName, prefixSize, dataWA, asn)
                    calculateTimeAW(msglist, prefixes, collectorName, prefixSize, dataAW, asn)
                    calculateChangesASPrefix(prefixes,ASes,msglist, collectorName)

                elif "FindPrefixThreshold" in action:
                    threshold = action.split("FindPrefixThreshold(")[1]
                    threshold = threshold[:-1]
                    findPrefixThreshold(collectorName,collectorName+"/reporttimeAW.txt",60)

                elif "PlotIXP" in action:
                    print('Ploting IXP informations',"\n")
                    plotIXPmsg()
                    plotIXPprefix()

                elif "PlotCDFtimes" in action:
                    aux = action.split("TXTtoMem(")[1]
                    aux = int(threshold[:-1])
                    threshold,nas,prefix=aux.split(',')
                    if (int(prefix) == 0):
                        prefix = ''
                    print('Ploting times CDF graphics',"\n")
                    plotCDF("WA",threshold,int(nas),'')
                    plotCDF("AW",threshold,int(nas),'')

                elif "plotCDFASPrefix" in action:
                    print('Ploting prefixes CDF graphics',"\n")
                    plotCDFASPrefix()

                elif "teste" in action:
                    #TODO add new functionalits on menu
                    #plotLifeTimeforEveryprefix
                    #findPrefixThreshold
                    #calculateAverageTimebyPrefix
                    #mostRepeatedPrefix
                    #highestTimes
                    #diffTable
                    return 0

                elif "help" in action:
                    help()
                elif "quit" in action:
                    print ("Quiting BGPstability")
                    os._exit(1)
                else:
                    print ("Invalid command. Type \'help\' to list the available commands.\n")

def help():
    print("List of BGPstability commands")
    print("TXTtoMem - read the txt files into memory")
    print("\t example: TXTtoMem(collectorName,pathtofile)")
    print("CountStatistics - ")
    print("\t example: CountStatistics()")
    print("CalculateAW - calculate the time between an announcement and a withdrawn")
    print("\t example: CalculateAW(prefixSize,ASN)")
    print("CalculateWA - calculate the time between a withdrawn and an announcement")
    print("\t example: CalculateWA(prefixSize,ASN)")
    print("CalculateChangesASPrefix - calculate how many changes every tuple(ases,prefix) have ")
    print("\t example: CalculateChangesASPrefix(prefixSize)")
    print("CalculateALL - CalculateAW + CalculateWA + CalculateChangesASPrefix")
    print("\t example: CalculateChangesALL(prefixSize,ASN)")
    print("FindPrefixThreshold - ")
    print("\t example: FindPrefixThreshold(file,threshold)")
    print("PlotIXP - ")
    print("\t example: PlotIXP()")
    print("PlotCDFtimes - ")
    print("\t example: PlotCDFtimes(threshold,ASN,prefix)")
    print("plotCDFASPrefix - ")
    print("\t example: plotCDFASPrefix()")
    print("quit - quits BGPstability")

if __name__ == '__main__':


    #wichPrefixHasChanged('AMSIX_010119_070119_new/reporttimeAW.txt')
    #averageTimeByPrefix('AMSIX_010119_070119_new/reporttimeAW.txt','104.237.191.0;24')
    #cli()
    announcement = 0
    withdrawn = 0
    msglist = []

    collectorName = sys.argv[1]
    path = sys.argv[2]
    numberas = sys.argv[3]

    print(collectorName)
    print(path)
    print(numberas)

    if not os.path.exists(collectorName):
        os.makedirs(collectorName)

    auxlist,ases,prefix,data = txttoMemory_new(path,collectorName)
    dataAW = copy.deepcopy(data)
    dataWA = copy.deepcopy(data)

    for i in data:
        announcement = len(data[i][0]) + announcement
        withdrawn = len(data[i][1]) + withdrawn

    print("announcements:")
    print(announcement)
    print("Withdrawals:")
    print(withdrawn)

    txtIXP(announcement+withdrawn,announcement,withdrawn,0,0,0,collectorName)

    ASes = {x:ases.count(x) for x in set(ases)}
    txtIXP2(ASes,collectorName)
    prefixes = {x:prefix.count(x) for x in set(prefix)}


    calculateTimeWA(msglist, prefixes, collectorName, 0, dataWA, int(numberas))
    calculateTimeAW(msglist, prefixes, collectorName, 0, dataAW, int(numberas))



    os._exit(1)
