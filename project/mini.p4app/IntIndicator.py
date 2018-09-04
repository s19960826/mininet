from scapy.all import *
import sys, os


class IntIndicator(Packet):
    name = "INT_On"
    fields_desc = [
        IntField("INT_set", 0),
    ]

class shim_header(Packet):
    name = "INT_shim_header"
    fields_desc = [
        ByteField("INT_header_type", 1),
        ByteField("rsvd", 0),
        ByteField("INT_data_length", 2),
        ByteField("rsvd", 0),
    ]

class int_header(Packet):
    name = "INT_header"
    fields_desc = [
        ByteField("ins_cnt",0),
        ByteField("max_hop_cnt", 5),
        ByteField("total_hop_cnt", 0),
        BitField("e",0x0, 1),
        BitField("inst_0",0x0,1),       # switch_id
        BitField("inst_1",0x0,1),       # deq_timedelta
        BitField("inst_2",0x0,1),       # enq_timestamp/enq_qdepth
        BitField("inst_3",0x0,1),       # ingress_global_timestamp
        BitField("rsvd", 0x0,3),
    ]                
bind_layers(TCP, IntIndicator)
bind_layers(IntIndicator,shim_header)
bind_layers(shim_header,int_header)


