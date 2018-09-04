#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr,bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from IntIndicator import IntIndicator,shim_header,int_header

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():

    if len(sys.argv) != 3 and len(sys.argv) != 7:
        print 'pass 2 arguments: <destination> "<message> <inst_0> <inst_1> <inst_2> <inst_3>"'
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print "sending on interface %s to %s" % (iface, str(addr))
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535))

    if len(sys.argv) == 7:
        pkt = pkt/IntIndicator(INT_set = 1)/shim_header()/int_header(ins_cnt = int(sys.argv[3])+int(sys.argv[4])+int(sys.argv[5])+int(sys.argv[6]),inst_0 = int(sys.argv[3]),inst_1 = int(sys.argv[4]),inst_2 = int(sys.argv[5]),inst_3 = int(sys.argv[6]))/sys.argv[2]
    else:
        pkt = pkt/IntIndicator()/shim_header()/int_header()/sys.argv[2]
    pkt.show2()
    print "len(pkt) = ", len(pkt)
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()
