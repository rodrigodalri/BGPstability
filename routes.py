#!/usr/bin/env python
import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

def main():

    if len(sys.argv) != 3:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    outputfile = sys.argv[2]+'.txt'

    timestamp = 0
    n_as = 0
    prefix = ''
    leng = 0

    d = Reader(sys.argv[1])

    for m in d:
        contents = ''
        m = m.mrt
        if m.type == MRT_T['BGP4MP'] \
            or m.type == MRT_T['BGP4MP_ET']:
                try:
                    if m.bgp.msg.type == BGP_MSG_T['UPDATE']:

                        #Withdrawn ipv4
                        if m.bgp.msg.wd_len != 0:
                            print('----------------------------------')
                            print('withdrawn')
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            f = open(outputfile, 'a+')
                            f.write('w;'+str(timestamp)+';'+str(n_as)+';')
                            f.close()
                            print(timestamp)
                            print(n_as)
                            for withdrawn in m.bgp.msg.withdrawn:
                                prefix = withdrawn.prefix
                                leng = withdrawn.plen
                                f = open(outputfile, 'a+')
                                f.write(str(prefix)+';'+str(leng)+';')
                                f.close()
                                print(prefix,leng)
                            f = open(outputfile, 'a+')
                            f.write('\n')
                            f.close()

                        #Withdrawn ipv6
                        if m.bgp.msg.attr_len != 0:
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            for attr in m.bgp.msg.attr:
                                if attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
                                    if 'withdrawn' in attr.mp_unreach:
                                        for withdrawn in attr.mp_unreach['withdrawn']:
                                            prefix = withdrawn.prefix
                                            leng = withdrawn.plen
                                            f = open(outputfile, 'a+')
                                            f.write('w;'+str(timestamp)+';'+str(n_as)+';'+str(prefix)+';'+str(leng)+';'+'\n')
                                            f.close()
                                            print('----------------------------------')
                                            print('withdrawn')
                                            print(timestamp)
                                            print(n_as)
                                            print(prefix, leng)
                                    #f = open(outputfile, 'a+')
                                    #f.write('\n')
                                    #f.close()

                        #announcement ipv6
                        if m.bgp.msg.attr_len != 0:
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            for attr in m.bgp.msg.attr:
                                if attr.type == BGP_ATTR_T['AS_PATH']:
                                    for path_seg in attr.as_path:
                                        as_path = path_seg['val']
                                elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
                                    if 'nlri' in attr.mp_reach:
                                        for nlri in attr.mp_reach['nlri']:
                                            prefix = nlri.prefix
                                            leng = nlri.plen
                                            f = open(outputfile, 'a+')
                                            f.write('a;'+str(timestamp)+';'+str(n_as)+';'+str(as_path)+';'+str(prefix)+';'+str(leng)+';'+'\n')
                                            f.close()
                                            print('----------------------------------')
                                            print('announcement')
                                            print(timestamp)
                                            print(n_as)
                                            print(as_path)
                                            print(prefix, leng)
                                    #f = open(outputfile, 'a+')
                                    #f.write('\n')
                                    #f.close()

                        #announcement ipv4
                        if m.bgp.msg.attr_len != 0:
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            for nlri in m.bgp.msg.nlri:
                                prefix = nlri.prefix
                                leng = nlri.plen
                                f = open(outputfile, 'a+')
                                f.write('a;'+str(timestamp)+';'+str(n_as)+';'+str(as_path)+';'+str(prefix)+';'+str(leng)+';')
                                f.close()
                                print('----------------------------------')
                                print('announcement')
                                print(timestamp)
                                print(n_as)
                                print(as_path)
                                print(prefix, leng)
                                f = open(outputfile, 'a+')
                                f.write('\n')
                                f.close()

                except:
                    #other messages
                    continue

if __name__ == '__main__':
    main()
