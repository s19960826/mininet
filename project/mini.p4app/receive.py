#!/usr/bin/env python
import sys
import struct
import os

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR
from IntIndicator import IntIndicator,shim_header,int_header

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def handle_pkt(pkt):
    if shim_header in pkt or (TCP in pkt and pkt[TCP].dport == 1234):
        print "got a packet1"
        pkt.show2()
        print "len(pkt) = ", len(pkt)
        if pkt[IntIndicator].INT_set == 1:
            dump_int(pkt)
        sys.stdout.flush()

def main():
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))

def dump_int(pkt):
    print "\n###[INT info]###\n"
    ind = 0
    for i in range(1,pkt[int_header].total_hop_cnt+1):
        if pkt[int_header].inst_0 == 1:
            print "Switch id = ", str(pkt[Raw]).encode("HEX")[ind:ind+8], "\n"
            ind = ind + 8
        if pkt[int_header].inst_1 == 1:
            print "Time in queue =", str(pkt[Raw]).encode("HEX")[ind:ind+8], "\n"    
            ind = ind + 8
        if pkt[int_header].inst_2 == 1:
            print "Enqueue Timestamp =", str(pkt[Raw]).encode("HEX")[ind:ind+6], "\n"    
            ind = ind + 6
            print "Queue Length =", str(pkt[Raw]).encode("HEX")[ind:ind+2], "\n"    
            ind = ind + 2
        if pkt[int_header].inst_3 == 1:
            print "Ingress Timestamp =", str(pkt[Raw]).encode("HEX")[ind:ind+8], "\n"    
            ind = ind + 8
        print "######\n"
    print "Payload = ", str(str(pkt[Raw]).encode("HEX")[ind:len(str(pkt[Raw]).encode("HEX"))]).decode("HEX")
    print "\n######"    
if __name__ == '__main__':
    main()
