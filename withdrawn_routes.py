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
                        if m.bgp.msg.wd_len != 0:
                            print('----------------------------------')
                            timestamp = m.ts
                            n_as = m.bgp.peer_as
                            f = open('withdrawn_routes.txt', 'a+')
                            f.write(str(timestamp)+';'+str(n_as)+';')
                            f.close()
                            print(timestamp)
                            print(n_as)
                            for withdrawn in m.bgp.msg.withdrawn:
                                prefix = withdrawn.prefix
                                leng = withdrawn.plen
                                f = open('withdrawn_routes.txt', 'a+')
                                f.write(str(prefix)+';'+str(leng)+';')
                                f.close()
                                print(prefix,leng)
                            f = open('withdrawn_routes.txt', 'a+')
                            f.write('\n')
                            f.close()
                except:
                    continue

if __name__ == '__main__':
    main()
