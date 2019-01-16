#!/usr/bin/env python
import os
import sys
import json
import threading
import subprocess
from datetime import *
#from mrtparse import *
import numpy as np
import matplotlib.pyplot as plt


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
        if ASnumber == i["as"]:
            if i["type"] == 'a':
                prefixList.append(i["prefix"])
                prefixListA.append(i["prefix"])
            else:
                prefixList.append(i["prefix"])
                prefixListW.append(i["prefix"])


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

#save in a txt file information about the IXP
def txtIXP(_totalMSG, _announcement, _withdrawn):

    totalMSG = _totalMSG
    announcement = _announcement
    withdrawn = _withdrawn

    f = open('reports/route-collector.decix-ham.fra.pch.net.txt', 'a+')
    #FORMAT: total_number_of_messages;number_of_announcements;number_of_withdrawns
    f.write(str(totalMSG)+';'+str(announcement)+';'+str(withdrawn)+'\n')
    f.close()

#save in a txt file information about the AS
def txtAS(_label, _msgA, _msgW, _prefix, _prefixA, _prefixW):

    label = _label
    msgA = _msgA
    msgW = _msgW
    prefix = _prefix
    prefixA = _prefixA
    prefixW = _prefixW

    label = 'reports/AS'+label+'.txt'
    f = open(label, 'a+')
    #FORMAT: total_number_of_messages;number_of_announcements;number_of_withdrawns;total_number_of_prefixes;announced_prefixes;withdrawed_prefixes
    f.write(str(msgA+msgW)+';'+str(msgA)+';'+str(msgW)+';'+str(prefix)+';'+str(prefixA)+';'+str(prefixW)+'\n')
    f.close()

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

    txtIXP(totalMSG,announcement,withdrawn)



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



def main():

    #reading the txt file into memory
    print('Reading the 20190101.txt file into memory.')
    msglist1 = txttoMemory('20190101.txt')
    print('Reading the 20190102.txt file into memory.')
    msglist2 = txttoMemory('20190102.txt')
    print("\n")

    #looking for which ASes sent messages
    ASes1 = countASes(msglist1)
    print("ASes found and number of occurrences in 20190101")
    print(ASes1)
    print("\n")

    #looking for which ASes sent messages
    ASes2 = countASes(msglist2)
    print("ASes found and number of occurrences in 20190102")
    print(ASes2)
    print("\n")

    print('Counting statistics and saving to a txt file')
    countStatistics(msglist1,ASes1)
    countStatistics(msglist2,ASes2)


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









    #------------------------------------------------------------------------------------------------------------------------------------

    #looking for which prefix
    #prefixes = countPrefix(msglist)
    #print("Prefixes found and number of occurrences.")
    #print(prefixes)
    #print("\n")


    #counting the types of messages of each prefix
    #for i in prefixes:
    #    print("Prefix: %s" % i)
    #    a,w = msgPrefix(i, msglist)
    #    print("announcements: %s" % a)
    #    print("withdrawns: %s" % w)
    #    print("\n")

    #list every aspath from every prefix
    #for i in prefixes:
    #    print("Prefix: %s" % i)
    #    print("Timestamp : AS : ASpath")
    #    aspathList = msgASPath(i,msglist)
    #    for j in aspathList:
    #        print(j)
    #    print("\n")

    #------------------------------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    main()
