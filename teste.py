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

#TODO check if you are picking up all the prefixes when there is more than one in the same message
#TODO some plots are out of date

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

#save in a txt file information about the IXP
def txtIXP(_totalMSG, _announcement, _withdrawn, _prefix, _prefixA, _prefixW):

    totalMSG = _totalMSG
    announcement = _announcement
    withdrawn = _withdrawn
    prefix = _prefix
    prefixA = _prefixA
    prefixW = _prefixW

    f = open('reports/route-collector.decix-ham.fra.pch.net.txt', 'a+')
    #FORMAT: total_number_of_messages;number_of_announcements;number_of_withdrawns;total_number_of_prefixes;announced_prefixes;withdrawed_prefixes
    f.write(str(totalMSG)+';'+str(announcement)+';'+str(withdrawn)+';'+str(prefix)+';'+str(prefixA)+';'+str(prefixW)+'\n')
    f.close()

#save in a txt file information about the AS
def txtAS(_label, _msgA, _msgW, _prefix, _prefixA, _prefixW):

    label = _label
    msgA = _msgA
    msgW = _msgW
    prefix = _prefix
    prefixA = _prefixA
    prefixW = _prefixW

    label = 'reports/AS'+str(label)+'.txt'
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
        if j["as"] == '43252' and j["type"] == 'a':
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
        if i["as"] == '43252' and i["type"] == 'a':
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
        if i["as"] == '43252' and i["type"] == 'a':
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
                if j.split(':')[1] == '43252':
                    list = j["aspath"].split(',')[0]
                    try:
                        asesList.append(int(list[2:-1]))
                    except:
                        asesList.append(int(list[2:-2]))
                else:
                    asesList.append(j.split(':')[1])
                changesList.append(j.split(':')[2])

    return({x:asesList.count(x) for x in set(asesList)},{y:changesList.count(y) for y in set(changesList)})
#------------------------------[PREFIX]-------------------------------------------


#------------------------------[STATISTIC]-------------------------------------------
#count statistics about IXP and ASes and save to a txt file
def countStatistics(_msgList, _ASes):

    totalMSG = 0
    announcement = 0
    withdrawn = 0

    ASes = _ASes
    msglist = _msgList

    for i in ASes:
        msgA,msgW = msgAS(i, msglist)
        prefix,prefixA,prefixW = prefixAS(i, msglist)

        txtAS(i,msgA,msgW,prefix,prefixA,prefixW)

        totalMSG = totalMSG + msgA + msgW
        announcement = announcement + msgA
        withdrawn = withdrawn + msgW

    prefix,prefixA,prefixW = prefixIXP(msglist)
    txtIXP(totalMSG,announcement,withdrawn,prefix,prefixA,prefixW)

#calculate the time between an announcement and a withdrawn
def calculateTimeAW(_msgList, _prefixes, _label):

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
                                dataA = datetime.fromtimestamp(int(j["timestamp"]))
                                dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                dataW = datetime.fromtimestamp(int(k["timestamp"]))
                                dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                time = dW - dA
                                find = 1
                                prefixList.append(i)
                                msglist.remove(j)
                                msglist.remove(k)
                                f = open('reports/timeAW'+label+'.txt', 'a+')
                                f.write(str(time)+'\n')
                                f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

#calculate the time between an withdrawn and a announcement
def calculateTimeWA(_msgList, _prefixes, _label):

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
                                dataW = datetime.fromtimestamp(int(j["timestamp"]))
                                dW = datetime.strptime(str(dataW), "%Y-%m-%d %H:%M:%S")
                                dataA = datetime.fromtimestamp(int(k["timestamp"]))
                                dA = datetime.strptime(str(dataA), "%Y-%m-%d %H:%M:%S")
                                time = dA - dW
                                find = 1
                                prefixList.append(i)
                                msglist.remove(j)
                                msglist.remove(k)
                                f = open('reports/timeWA'+label+'.txt', 'a+')
                                f.write(str(time)+'\n')
                                f.close()

    prefix = {x:prefixList.count(x) for x in set(prefixList)}

    return prefix

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

#calculate how many changes and how many cars announced each prefix
def calculateChangesPrefix(_prefixes, _msglist, _label):

    prefixes = _prefixes
    msglist = _msglist
    label = _label
    for i in prefixes:
        var1,var2 = prefixChanges(i, prefixes, msglist)
        txtPrefix(i,len(var1),len(var2), label)
#------------------------------[STATISTIC]-------------------------------------------


#------------------------------[PLOT]---------------------------------------------
#TODO plots are out of date
def plotIXP(_totalMSG1,_announcement1,_withdrawn1,_label1,_totalMSG2,_announcement2,_withdrawn2,_label2):

    totalMSG1 = _totalMSG1
    announcement1 = _announcement1
    withdrawn1 = _withdrawn1
    label1 = _label1
    totalMSG2 = _totalMSG2
    announcement2 = _announcement2
    withdrawn2 = _withdrawn2
    label2 = _label2

    day1 = (totalMSG1, announcement1, withdrawn1)
    day2 = (totalMSG2, announcement2, withdrawn2)

    ind = np.arange(len(day1))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, day1, width, color='SkyBlue', label=label1)
    rects2 = ax.bar(ind + width/2, day2, width, color='IndianRed', label=label2)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of Messages')
    ax.set_title('BGP Messages - DECIX Route Collector')
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total', 'Announcement', 'Withdrawn'))
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

    plt.show()
def plotASmsg(_ASN,_totalMSG1,_announcement1,_withdrawn1,_label1,_totalMSG2,_announcement2,_withdrawn2,_label2):

    ASN = _ASN
    totalMSG1 = _totalMSG1
    announcement1 = _announcement1
    withdrawn1 = _withdrawn1
    label1 = _label1
    totalMSG2 = _totalMSG2
    announcement2 = _announcement2
    withdrawn2 = _withdrawn2
    label2 = _label2

    day1 = (totalMSG1, announcement1, withdrawn1)
    day2 = (totalMSG2, announcement2, withdrawn2)

    ind = np.arange(len(day1))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, day1, width, color='SkyBlue', label=label1)
    rects2 = ax.bar(ind + width/2, day2, width, color='IndianRed', label=label2)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of Messages')
    ax.set_title('BGP Messages of AS%s' % ASN)
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total', 'Announcement', 'Withdrawn'))
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

    plt.show()
def plotASprefix(_ASN,_totalPrefix1,_aPrefix1,_wPrefix1,_label1,_totalPrefix2,_aPrefix2,_wPrefix2,_label2):

    ASN = _ASN
    totalPrefix1 = _totalPrefix1
    aPrefix1 = _aPrefix1
    wPrefix1 = _wPrefix1
    label1 = _label1
    totalPrefix2 = _totalPrefix2
    aPrefix2 = _aPrefix2
    wPrefix2 = _wPrefix2
    label2 = _label2

    day1 = (totalPrefix1, aPrefix1, wPrefix1)
    day2 = (totalPrefix2, aPrefix2, wPrefix2)

    ind = np.arange(len(day1))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width/2, day1, width, color='SkyBlue', label=label1)
    rects2 = ax.bar(ind + width/2, day2, width, color='IndianRed', label=label2)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Number of Prefixes')
    ax.set_title('Prefixes announced/withdrawed by AS%s' % ASN)
    ax.set_xticks(ind)
    ax.set_xticklabels(('Total', 'Announceds', 'Withdraweds'))
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

    plt.show()
#TODO plots are out of date

#plot times between messages AW and WA
def plotCDF(_path, _type):

    path = _path
    type = _type
    timeList = []
    count = 0

    save = path.split(".")[0]
    save = "figures/"+save.split("/")[1]

    if type == "W-A":
        name = "DECIX Route Collector " + save.split("figures/timeWA")[1]
    else:
        name = "DECIX Route Collector " + save.split("figures/timeAW")[1]

    with open(path) as fp:
        line = fp.readline()
        while line:
            h = int(line.split(":")[0])
            m = int(line.split(":")[1])
            s = int(line.split(":")[2])
            timeList.append(m + h*60)
            line = fp.readline()


    count = len(timeList)

    pylab.plot(np.sort(timeList),np.arange(len(timeList))/float(len(timeList)-1), label="Time between "+type,  linewidth=2)
    pylab.title(name + " - "+str(count) + " occurrences", loc='center')
    pylab.ylabel("Frequency", fontsize=18)
    pylab.xlabel("Time (m)", fontsize=18)
    pylab.grid(True)
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=14)
    pylab.savefig(save+".pdf", dpi=600)
    pylab.savefig(save+".png", dpi=600)
    pylab.clf()

#plot number of changes in aspath
def plotCDFPrefix(_path):

    path = _path
    changesList = []
    count = 0

    save = path.split(".")[0]
    save = "figures/"+save.split("/")[1]

    with open(path) as fp:
        line = fp.readline()
        while line:
            num = int(line.split(";")[3])
            changesList.append(num)
            line = fp.readline()

    count = len(changesList)

    pylab.plot(np.sort(changesList),np.arange(len(changesList))/float(len(changesList)-1), label='number of changes',  linewidth=2)
    pylab.title(str(count) + " occurrences", loc='center')
    pylab.ylabel("Frequency", fontsize=18)
    pylab.xlabel("ASPATH changes (n)", fontsize=18)
    pylab.grid(True)
    pylab.xlim(0, )
    pylab.ylim(0, 1)
    pylab.legend(loc="best", fontsize=14)
    pylab.savefig(save+".pdf", dpi=600)
    pylab.savefig(save+".png", dpi=600)
    pylab.clf()
#------------------------------[PLOT]---------------------------------------------



def main():

    #reading the txt file into memory
    print('Reading the 20190101.txt file into memory.',"\n")
    msglist1 = txttoMemory('20190101.txt')
    print('Reading the 20190102.txt file into memory.',"\n")
    msglist2 = txttoMemory('20190102.txt')

    #looking for which ASes sent messages
    ASes1 = countASes(msglist1)
    print("ASes found and number of occurrences in 20190101")
    print(ASes1,"\n")

    #looking for which ASes sent messages
    ASes2 = countASes(msglist2)
    print("ASes found and number of occurrences in 20190102")
    print(ASes2,"\n")

    print('Counting statistics and saving to a txt file',"\n")
    #countStatistics(msglist1,ASes1)
    #countStatistics(msglist2,ASes2)

    #TODO plots are out of date ---------------------------------------------------------------------------------------------------------
    #plot ASes graphics
    #j = 0
    #for i in ASes:
        #plotASmsg(asN[j],total1[j],announcements1[j],withdrawns1[j],'2019-01-01',total2[j],announcements2[j],withdrawns2[j],'2019-01-02')
        #plotASprefix(asN[j],pre1[j],preA1[j],preW1[j],'2019-01-01',pre2[j],preA2[j],preW2[j],'2019-01-02')
        #j = j+1

    #plot IXP graphic
    #plotIXP(totalMSG1,announcement1,withdrawn1,'2019-01-01',totalMSG2,announcement2,withdrawn2,'2019-01-02')
    #TODO plots are out of date ---------------------------------------------------------------------------------------------------------


    print('Looking for which prefix',"\n")
    prefixes1 = countPrefix(msglist1)
    prefixes2 = countPrefix(msglist2)

    print('Calculating the time between an announcement and a withdrawn',"\n")
    calculateTimeAW(msglist1, prefixes1, '20190101')
    calculateTimeAW(msglist2, prefixes2, '20190102')
    #calculateTimeA(msglist1, prefixes1, '20190101')
    #calculateTimeA(msglist2, prefixes2, '20190102')

    print('Calculating the time between an withdrawn and a announcement',"\n")
    calculateTimeWA(msglist1, prefixes1, '20190101')
    calculateTimeWA(msglist2, prefixes2, '20190102')
    #calculateTimeW(msglist1, prefixes1, '20190101')
    #calculateTimeW(msglist2, prefixes2, '20190102')

    print('Ploting CDF graphics',"\n")
    plotCDF("reports/timeWA20190101.txt", "W-A")
    plotCDF("reports/timeWA20190102.txt", "W-A")
    plotCDF("reports/timeAW20190101.txt", "A-W")
    plotCDF("reports/timeAW20190102.txt", "A-W")

    print('Calculating the changes of each prefix',"\n")
    calculateChangesPrefix(prefixes1,msglist1, '20190101')
    calculateChangesPrefix(prefixes2,msglist2, '20190102')

    print('Ploting prefixes CDF graphics',"\n")
    plotCDFPrefix("reports/prefixes20190101.txt")
    plotCDFPrefix("reports/prefixes20190102.txt")



if __name__ == '__main__':
    main()
