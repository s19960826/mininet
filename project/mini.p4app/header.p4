#ifndef __HEADER_H__
#define __HEADER_H__ 1

struct ingress_metadata_t {
    bit<32> nhop_ipv4;
}

struct intrinsic_metadata_t {
    bit<48> ingress_global_timestamp;
    bit<32> lf_field_list;
    bit<16> mcast_grp;
    bit<16> egress_rid;

}

struct int_metadata_t {
    bit<16> insert_byte_cnt;
    bit<8> int_hdr_word_len;
    bit<32> switch_id; 
}

struct metadata {
    ingress_metadata_t   ingress_metadata;
    /*intrinsic_metadata_t intrinsic_metadata;*/
    int_metadata_t int_metadata;
}

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header type_t {
    bit<32> int_set;
}

header int_shim_t {
    bit<8> int_type;  /*destination based or hop-by-hop*/
    bit<8> rsvd1;
    bit<8> len;       /*length of INTmetadata+INTstack+shim+tail*/ 
    bit<8> rsvd2;
}

header int_header_t {
    bit<8> ins_cnt;
    bit<8> max_hop_cnt;
    bit<8> total_hop_cnt;
    bit<1> e;
    bit<1> inst_0;    /*switch_id*/
    bit<1> inst_1;    /*hop_latency*/ 
    bit<1> inst_2;    /*q_info*/
    bit<1> inst_3;    /*ingress_timestamp*/
    bit<3> rsvd2;    
}

header int_switch_id_t {
    bit<32> switch_id; 
}

header int_hop_latency_t {
    bit<32> hop_latency;
}

header int_q_info_t {
    bit<24> q_time; 
    bit<8> q_length;
}

header int_ingress_tstamp_t {
    bit<32> ingress_tstamp;
}



struct headers {
    ethernet_t                  ethernet;
    ipv4_t                      ipv4;
    tcp_t                       tcp;
    type_t                      type;
    int_shim_t                  int_shim;
    int_header_t                int_header;
    int_switch_id_t             int_switch_id;
    int_hop_latency_t           int_hop_latency;
    int_q_info_t                int_q_info; 
    int_ingress_tstamp_t        int_ingress_tstamp;
}


#endif // __HEADER_H__
