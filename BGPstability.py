#!/usr/bin/env python
import os
import sys
import json
import threading
import subprocess
from datetime import *
import numpy as np
import matplotlib.pyplot as plt
import pylab
import ipaddress

#AS43252 is decix
#AS62972 is amsix

#TODO check if you are picking up all the prefixes when there is more than one in the same message
#TODO some plots are out of date
#TODO add threshold time in CDF AW and WA plots
#TODO add prefix size in "Calculates"

#-----------------------------[FILE]----------------------------------------------
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
#TODO more than one prefix for message
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

    if network1.overlaps(network2):
        print("isAggregate", "\n")
        print(prefix1, prefix2)
        return 1
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
def calculateTimeAW(_msgList, _prefixes, _label, _prefixSize):

    prefixes = _prefixes
    msglist = _msgList
    label = _label
    prefixSize = _prefixSize

    prefix = {}
    prefixList =[]

    time = 0
    find = 0
    all = 0

    if int(prefixSize) == 0:
        all = 1

    for i in prefixes:
        if (i.split(';')[1] == prefixSize or all == 1):
            for j in msglist:
                find = 0
                if i == j["prefix"] and j["type"] == 'a':
                    for k in msglist:
                        if k["type"] == 'w' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
                            list = k["prefix"].split(';')
                            for l in range(0,len(list)-1,2):
                                if i == list[l]+';'+list[l+1]:
                                    dataA = datetime.fromtimestamp(int(j["timestamp"]))
                                    dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                    dataW = datetime.fromtimestamp(int(k["timestamp"]))
                                    dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                    time = dW - dA
                                    find = 1
                                    prefixList.append(i)
                                    msglist.remove(j)
                                    msglist.remove(k)
                                    f = open(str(label)+'/reporttimeAW.txt', 'a+')
                                    f.write(str(time)+'\n')
                                    f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#calculate the time between an withdrawn and a announcement
def calculateTimeWA(_msgList, _prefixes, _label, _prefixSize):

    prefixes = _prefixes
    msglist = _msgList
    label = _label
    prefixSize = _prefixSize

    prefix = {}
    prefixList =[]

    time = 0
    find = 0
    all = 0

    if int(prefixSize) == 0:
        all = 1

    for i in prefixes:
        if (i.split(';')[1] == prefixSize or all == 1):
            for j in msglist:
                find = 0
                if j["type"] == 'w':
                    list = j["prefix"].split(';')
                    for l in range(0,len(list)-1,2):
                        if i == list[l]+';'+list[l+1]:
                            for k in msglist:
                                if i == k["prefix"] and k["type"] == 'a' and find == 0 and int(k["timestamp"]) >= int(j["timestamp"]):
                                    dataW = datetime.fromtimestamp(int(j["timestamp"]))
                                    dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                    dataA = datetime.fromtimestamp(int(k["timestamp"]))
                                    dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                    time = dA - dW
                                    find = 1
                                    prefixList.append(i)
                                    msglist.remove(j)
                                    msglist.remove(k)
                                    f = open(str(label)+'/reporttimeWA.txt', 'a+')
                                    f.write(str(time)+'\n')
                                    f.close()

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

#calculate how many changes and how many ases announced each prefix
def calculateChangesPrefix(_prefixes, _msglist, _label):

    prefixes = _prefixes
    msglist = _msglist
    label = _label
    for i in prefixes:
        var1,var2 = prefixChanges(i, prefixes, msglist)
        txtPrefix(i,len(var1),len(var2), label)

#calculate how many changes every tupleo(ases,prefix) have
def calculateChangesASPrefix(_prefixes, _ases, _msglist, _label):

    prefixes = _prefixes
    msglist = _msglist
    label = _label
    ases = _ases
    prefixSize = _prefixSize

    for i in prefixes:
        for j in ases:
            var1 = prefixASChanges(i, j, prefixes, msglist)
            if len(var1) != 0:
                txtPrefix2(i,j,len(var1),label)
#------------------------------[STATISTIC]-------------------------------------------

#------------------------------[PLOT]---------------------------------------------
#plot information about the IXP
def plotIXP(_path):

    path = _path

    d1 = []
    d2 = []
    d3 = []
    d4 = []
    d5 = []
    d6 = []
    d7 = []

    with open(path) as fp:
        line = fp.readline()
        d1.append(int(line.split(";")[0]))
        d1.append(int(line.split(";")[1]))
        d1.append(int(line.split(";")[2]))
        d1.append(int(line.split(";")[3]))
        d1.append(int(line.split(";")[4]))
        d1.append(int(line.split(";")[5]))

        line = fp.readline()
        d2.append(int(line.split(";")[0]))
        d2.append(int(line.split(";")[1]))
        d2.append(int(line.split(";")[2]))
        d2.append(int(line.split(";")[3]))
        d2.append(int(line.split(";")[4]))
        d2.append(int(line.split(";")[5]))

        line = fp.readline()
        d3.append(int(line.split(";")[0]))
        d3.append(int(line.split(";")[1]))
        d3.append(int(line.split(";")[2]))
        d3.append(int(line.split(";")[3]))
        d3.append(int(line.split(";")[4]))
        d3.append(int(line.split(";")[5]))

        line = fp.readline()
        d4.append(int(line.split(";")[0]))
        d4.append(int(line.split(";")[1]))
        d4.append(int(line.split(";")[2]))
        d4.append(int(line.split(";")[3]))
        d4.append(int(line.split(";")[4]))
        d4.append(int(line.split(";")[5]))

        line = fp.readline()
        d5.append(int(line.split(";")[0]))
        d5.append(int(line.split(";")[1]))
        d5.append(int(line.split(";")[2]))
        d5.append(int(line.split(";")[3]))
        d5.append(int(line.split(";")[4]))
        d5.append(int(line.split(";")[5]))

        line = fp.readline()
        d6.append(int(line.split(";")[0]))
        d6.append(int(line.split(";")[1]))
        d6.append(int(line.split(";")[2]))
        d6.append(int(line.split(";")[3]))
        d6.append(int(line.split(";")[4]))
        d6.append(int(line.split(";")[5]))

        line = fp.readline()
        d7.append(int(line.split(";")[0]))
        d7.append(int(line.split(";")[1]))
        d7.append(int(line.split(";")[2]))
        d7.append(int(line.split(";")[3]))
        d7.append(int(line.split(";")[4]))
        d7.append(int(line.split(";")[5]))


    ind = np.arange(len(d1))  # the x locations for the groups
    width = 0.12  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - 3*width, d1, width, color='SkyBlue', label='2019/01/01')
    rects2 = ax.bar(ind - 2*width, d2, width, color='IndianRed', label='2019/01/02')
    rects3 = ax.bar(ind - width, d3, width, color='Chocolate', label='2019/01/03')
    rects4 = ax.bar(ind, d4, width, color='Orange', label='2019/01/04')
    rects5 = ax.bar(ind + width, d5, width, color='Olive', label='2019/01/05')
    rects6 = ax.bar(ind + 2*width, d6, width, color='Yellow', label='2019/01/06')
    rects7 = ax.bar(ind + 3*width, d7, width, color='Green', label='2019/01/07')


    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of')
    ax.set_title('BGP Messages - AMSIX Route Collector')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total Messages', 'Announcement Messages', 'Withdrawn Messages', 'Total Prefixes', 'Announced Prefixes', 'Withdrawed Prefixes'))
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
    autolabel(rects2, "left")
    autolabel(rects3, "center")
    autolabel(rects4, "center")
    autolabel(rects5, "center")
    autolabel(rects6, "center")
    autolabel(rects7, "center")

    plt.show()
    plt.savefig("figures/newIXP.pdf", dpi=600)
    plt.savefig("figures/newIXP.png", dpi=600)
    plt.clf()

#plot times between messages AW and WA
def plotCDF(_type):

    pathWA1 = "reports/timeWA20190101.txt"
    pathWA2 = "reports/timeWA20190102.txt"
    pathWA3 = "reports/timeWA20190103.txt"
    pathWA4 = "reports/timeWA20190104.txt"
    pathWA5 = "reports/timeWA20190105.txt"
    pathWA6 = "reports/timeWA20190106.txt"
    pathWA7 = "reports/timeWA20190107.txt"

    pathAW1 = "reports/timeAW20190101.txt"
    pathAW2 = "reports/timeAW20190102.txt"
    pathAW3 = "reports/timeAW20190103.txt"
    pathAW4 = "reports/timeAW20190104.txt"
    pathAW5 = "reports/timeAW20190105.txt"
    pathAW6 = "reports/timeAW20190106.txt"
    pathAW7 = "reports/timeAW20190107.txt"

    path1 = ""
    path2 = ""
    path3 = ""
    path4 = ""
    path5 = ""
    path6 = ""
    path7 = ""

    type = _type
    timeList1 = []
    timeList2 = []
    timeList3 = []
    timeList4 = []
    timeList5 = []
    timeList6 = []
    timeList7 = []
    count = 0

    if type == "W-A":
        #name = "DECIX Route Collector time WA"
        name = "an Withdrawn and a Announcement"
        path1 = pathWA1
        path2 = pathWA2
        path3 = pathWA3
        path4 = pathWA4
        path5 = pathWA5
        path6 = pathWA6
        path7 = pathWA7
        save = "figures/timeWA"
    else:
        #name = "DECIX Route Collector time AW"
        name = "an Announcement and a Withdrawn"
        path1 = pathAW1
        path2 = pathAW2
        path3 = pathAW3
        path4 = pathAW4
        path5 = pathAW5
        path6 = pathAW6
        path7 = pathAW7
        save = "figures/timeAW"

    with open(path1) as fp:
        line = fp.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList1.append(m + h*60)
            line = fp.readline()

    with open(path2) as fp2:
        line = fp2.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList2.append(m + h*60)
            line = fp2.readline()

    with open(path3) as fp3:
        line = fp3.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList3.append(m + h*60)
            line = fp3.readline()

    with open(path4) as fp4:
        line = fp4.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList4.append(m + h*60)
            line = fp4.readline()

    with open(path5) as fp5:
        line = fp5.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList5.append(m + h*60)
            line = fp5.readline()

    with open(path6) as fp6:
        line = fp6.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList6.append(m + h*60)
            line = fp6.readline()

    with open(path7) as fp7:
        line = fp7.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList7.append(m + h*60)
            line = fp7.readline()

    pylab.plot(np.sort(timeList1),np.arange(len(timeList1))/float(len(timeList1)-1), color='SkyBlue', label="2019/01/01 - "+ str(len(timeList1)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(timeList2),np.arange(len(timeList2))/float(len(timeList2)-1), color='IndianRed', label="2019/01/02 - "+ str(len(timeList2)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(timeList3),np.arange(len(timeList3))/float(len(timeList3)-1), color='Chocolate', label="2019/01/03 - "+ str(len(timeList3)),  linewidth=2, linestyle='-.')
    pylab.plot(np.sort(timeList4),np.arange(len(timeList4))/float(len(timeList4)-1), color='Orange', label="2019/01/04 - "+ str(len(timeList4)),  linewidth=2, linestyle=':')
    pylab.plot(np.sort(timeList5),np.arange(len(timeList5))/float(len(timeList5)-1), color='Olive', label="2019/01/05 - "+ str(len(timeList5)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(timeList6),np.arange(len(timeList6))/float(len(timeList6)-1), color='Yellow', label="2019/01/06 - "+ str(len(timeList6)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(timeList7),np.arange(len(timeList7))/float(len(timeList7)-1), color='Green', label="2019/01/07 - "+ str(len(timeList7)),  linewidth=2, linestyle='-.')
    pylab.title("Time between " + name, loc='center')
    pylab.ylabel("Frequency", fontsize=10)
    pylab.xlabel("Time (min)", fontsize=10)
    pylab.grid(True)
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=10)
    pylab.savefig(save+".pdf", dpi=600)
    pylab.savefig(save+".png", dpi=600)
    pylab.clf()

#plot number of changes in aspath
def plotCDFPrefix():

    path1 = "reports/prefixes20190101.txt"
    path2 = "reports/prefixes20190102.txt"
    path3 = "reports/prefixes20190103.txt"
    path4 = "reports/prefixes20190104.txt"
    path5 = "reports/prefixes20190105.txt"
    path6 = "reports/prefixes20190106.txt"
    path7 = "reports/prefixes20190107.txt"
    changesList1 = []
    changesList2 = []
    changesList3 = []
    changesList4 = []
    changesList5 = []
    changesList6 = []
    changesList7 = []

    count = 0

    save = "figures/prefixes"

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

    with open(path5) as fp5:
        line = fp5.readline()
        while line:
            num = int(line.split(";")[3])
            changesList5.append(num)
            line = fp5.readline()

    with open(path6) as fp6:
        line = fp6.readline()
        while line:
            num = int(line.split(";")[3])
            changesList6.append(num)
            line = fp6.readline()

    with open(path7) as fp7:
        line = fp7.readline()
        while line:
            num = int(line.split(";")[3])
            changesList7.append(num)
            line = fp7.readline()

    pylab.plot(np.sort(changesList1),np.arange(len(changesList1))/float(len(changesList1)-1), label='2019/01/01 - ' + str(len(changesList1)),  linewidth=2)
    pylab.plot(np.sort(changesList2),np.arange(len(changesList2))/float(len(changesList2)-1), label='2019/01/02 - ' + str(len(changesList2)),  linewidth=2)
    pylab.plot(np.sort(changesList3),np.arange(len(changesList3))/float(len(changesList3)-1), label='2019/01/02 - ' + str(len(changesList3)),  linewidth=2)
    pylab.plot(np.sort(changesList4),np.arange(len(changesList4))/float(len(changesList4)-1), label='2019/01/02 - ' + str(len(changesList4)),  linewidth=2)
    pylab.plot(np.sort(changesList5),np.arange(len(changesList5))/float(len(changesList5)-1), label='2019/01/02 - ' + str(len(changesList5)),  linewidth=2)
    pylab.plot(np.sort(changesList6),np.arange(len(changesList6))/float(len(changesList6)-1), label='2019/01/02 - ' + str(len(changesList6)),  linewidth=2)
    pylab.plot(np.sort(changesList7),np.arange(len(changesList7))/float(len(changesList7)-1), label='2019/01/02 - ' + str(len(changesList7)),  linewidth=2)
    pylab.title("Prefix - ASPATH Changes", loc='center')
    pylab.ylabel("Frequency", fontsize=18)
    pylab.xlabel("Changes (n)", fontsize=18)
    pylab.grid(True)
    plt.xticks(np.arange(min(changesList2), max(changesList2)+1, 1.0))
    pylab.xlim(0, 20)
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=12)
    pylab.savefig(save+".pdf", dpi=600)
    pylab.savefig(save+".png", dpi=600)
    pylab.clf()

#plot number of changes in aspath
def plotCDFASPrefix():

    path1 = "reports/prefixesAS20190101.txt"
    path2 = "reports/prefixesAS20190102.txt"
    path3 = "reports/prefixesAS20190103.txt"
    path4 = "reports/prefixesAS20190104.txt"
    path5 = "reports/prefixesAS20190105.txt"
    path6 = "reports/prefixesAS20190106.txt"
    path7 = "reports/prefixesAS20190107.txt"

    changesList1 = []
    changesList2 = []
    changesList3 = []
    changesList4 = []
    changesList5 = []
    changesList6 = []
    changesList7 = []
    count = 0

    save = "figures/prefixesAS"

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

    with open(path5) as fp5:
        line = fp5.readline()
        while line:
            num = int(line.split(";")[3])
            changesList5.append(num)
            line = fp5.readline()

    with open(path6) as fp6:
        line = fp6.readline()
        while line:
            num = int(line.split(";")[3])
            changesList6.append(num)
            line = fp6.readline()

    with open(path7) as fp7:
        line = fp7.readline()
        while line:
            num = int(line.split(";")[3])
            changesList7.append(num)
            line = fp7.readline()


    pylab.plot(np.sort(changesList1),np.arange(len(changesList1))/float(len(changesList1)-1), color='SkyBlue', label='2019/01/01 - ' + str(len(changesList1)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(changesList2),np.arange(len(changesList2))/float(len(changesList2)-1), color='IndianRed', label='2019/01/02 - ' + str(len(changesList2)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(changesList3),np.arange(len(changesList3))/float(len(changesList3)-1), color='Chocolate', label='2019/01/03 - ' + str(len(changesList3)),  linewidth=2, linestyle='-.')
    pylab.plot(np.sort(changesList4),np.arange(len(changesList4))/float(len(changesList4)-1), color='Orange', label='2019/01/04 - ' + str(len(changesList4)),  linewidth=2, linestyle=':')
    pylab.plot(np.sort(changesList5),np.arange(len(changesList5))/float(len(changesList5)-1), color='Olive', label='2019/01/05 - ' + str(len(changesList5)),  linewidth=2, linestyle='-')
    pylab.plot(np.sort(changesList6),np.arange(len(changesList6))/float(len(changesList6)-1), color='Yellow', label='2019/01/06 - ' + str(len(changesList6)),  linewidth=2, linestyle='--')
    pylab.plot(np.sort(changesList7),np.arange(len(changesList7))/float(len(changesList7)-1), color='Green', label='2019/01/07 - ' + str(len(changesList7)),  linewidth=2, linestyle='-.')
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
#------------------------------[PLOT]---------------------------------------------

def cli():
    while True:
        action = input("BGPstability: ")
        if len(action) > 0:
                if "TXTtoMem" in action:
                    msglist = []
                    aux = action.split("TXTtoMem(")[1]
                    aux = aux[:-1]
                    aux = aux.split(",")
                    collectorName = aux[0]
                    numberDays = aux[1]

                    if not os.path.exists(collectorName):
                        os.makedirs(collectorName)

                    for i in range(0, int(numberDays)):
                        auxlist = txttoMemory(aux[i+2])
                        msglist = msglist + auxlist

                    print("Looking for which ASes sent messages","\n")
                    ASes = countASes(msglist)
                    print('Looking for which prefix',"\n")
                    prefixes = countPrefix(msglist)
                    print('Counting statistics and saving to a txt file',"\n")
                    countStatistics(msglist,ASes,collectorName)

                elif "CalculateAW" in action:
                    prefixSize = action.split("CalculateAW(")[1]
                    prefixSize = prefixSize[:-1]
                    print('Calculating the time between an announcement and a withdrawn',"\n")
                    calculateTimeAW(msglist, prefixes, collectorName, prefixSize)

                elif "CalculateWA" in action:
                    prefixSize = action.split("CalculateWA(")[1]
                    prefixSize = prefixSize[:-1]
                    print('Calculating the time between an withdrawn and a announcement',"\n")
                    calculateTimeWA(msglist, prefixes, collectorName, prefixSize)

                elif "CalculateChangesASPrefix" in action:
                    prefixSize = action.split("CalculateChangesASPrefix(")[1]
                    prefixSize = prefixSize[:-1]
                    print('Calculating the changes of each (prefix,AS)',"\n")
                    calculateChangesASPrefix(prefixes,ASes,msglist, collectorName)

                elif "CalculateALL" in action:
                    prefixSize = action.split("CalculateALL(")[1]
                    prefixSize = prefixSize[:-1]
                    print('Calculating the changes of each (prefix,AS)',"\n")
                    calculateTimeAW(msglist, prefixes, collectorName, prefixSize)
                    calculateTimeWA(msglist, prefixes, collectorName, prefixSize)
                    calculateChangesASPrefix(prefixes,ASes,msglist, collectorName)

                elif "Plot" in action:
                    print('Ploting prefixes CDF graphics',"\n")
                    #plotCDFPrefix()
                    #plotCDFASPrefix()
                    print('Ploting IXP informations',"\n")
                    #plotIXP("reports/route-collector.decix-ham.fra.pch.net.txt")
                    #plotIXP("reports/route-collector.amsix-ord.pch.net.txt")
                    print('Ploting ASes informations',"\n")
                    #printASes(ASes1,"20190101")
                    print('Ploting times CDF graphics',"\n")
                    #TODO add threshold time in CDF AW and WA plots
                    #TODO fix day times
                    #plotCDF("W-A")
                    #plotCDF("A-W")
                    print('Ploting prefixes CDF graphics',"\n")
                    #plotCDFPrefix()
                    #plotCDFASPrefix()

                elif "help" in action:
                    help()
                elif "quit" in action:
                    print ("Quiting Dynam-IX")
                    #logs.close()
                    os._exit(1)
                else:
                    print ("Invalid command. Type \'help\' to list the available commands.\n")

def help():
    print("List of BGPstability commands")
    print("TXTtoMem - read the txt files into memory")
    print("\t\t example: TXTtoMem(collectorName,numberDays,pathtofile1,pathtofile2...)")
    print("CalculateAW - calculate the time between an announcement and a withdrawn")
    print("\t\t example: CalculateAW(prefixSize)")
    print("CalculateWA - calculate the time between an withdrawn and a announcement")
    print("\t\t example: CalculateWA(prefixSize)")
    print("CalculateChangesASPrefix - calculate how many changes every tupleo(ases,prefix) have ")
    print("\t\t example: CalculateChangesASPrefix(prefixSize)")
    print("CalculateChangesALL - CalculateAW + CalculateWA + CalculateChangesASPrefix")
    print("\t\t example: CalculateChangesALL(prefixSize)")
    print("quit - quits BGPstability")

if __name__ == '__main__':
    #main()
    threads = []
    t = threading.Thread(target=cli)
    threads.append(t)
    t.start()
