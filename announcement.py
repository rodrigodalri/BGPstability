#!/usr/bin/env python
import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

def main():

    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    timestamp = 0
    n_as = 0
    as_path = ''
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
                                            f = open('announcement.txt', 'a+')
                                            f.write('a;'+str(timestamp)+';'+str(n_as)+';'+str(as_path)+';'+str(prefix)+';'+str(leng)+';')
                                            f.close()
                                            print('----------------------------------')
                                            print('announcement')
                                            print(timestamp)
                                            print(n_as)
                                            print(as_path)
                                            print(prefix, leng)
                                    f = open('announcement.txt', 'a+')
                                    f.write('\n')
                                    f.close()

                        #announcement ipv4
                        if m.bgp.msg.attr_len != 0:
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            for nlri in m.bgp.msg.nlri:
                                prefix = nlri.prefix
                                leng = nlri.plen
                                f = open('announcement.txt', 'a+')
                                f.write('a;'+str(timestamp)+';'+str(n_as)+';'+str(as_path)+';'+str(prefix)+';'+str(leng)+';')
                                f.close()
                                print('----------------------------------')
                                print('announcement')
                                print(timestamp)
                                print(n_as)
                                print(as_path)
                                print(prefix, leng)
                                f = open('announcement.txt', 'a+')
                                f.write('\n')
                                f.close()

                except:
                    #other messages
                    continue

if __name__ == '__main__':
    main()
