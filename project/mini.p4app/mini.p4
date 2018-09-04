#include <core.p4>
#include <v1model.p4>

#include "header.p4"
#include "parser.p4"

/*control Int_inst_insert(inout headers hdr,inout standard_metadata_t standard_metadata, inout metadata meta) {
    action inst0_set_switch_id() {
        hdr.int_switch_id.setValid();
        hdr.int_switch_id.switch_id = meta.int_metadata.switch_id;
    }
    action inst1_set_hop_latency() {
        hdr.int_hop_latency.setValid();
        hdr.int_hop_latency.hop_latency = (bit<32>) standard_metadata.deq_timedelta;
    }
    action inst2_set_q_info() {
        hdr.int_q_info.setValid();
        //hdr.int_q_occupancy.q_id = (bit<8>) standard_metadata.egress_qid;
        hdr.int_q_info.q_time = (bit<16>) standard_metadata.enq_timestamp;        
        hdr.int_q_info.q_length = (bit<16>) standard_metadata.enq_qdepth;
    }
    action inst3_set_ingress_tstamp() {
        hdr.int_ingress_tstamp.setValid();
        hdr.int_ingress_tstamp.ingress_tstamp = (bit<32>) standard_metadata.ingress_global_timestamp;
    }
    table inst0_map {
        actions = {
            inst0_set_switch_id();
            NoAction;
        }
        key = {
            hdr.int_header.inst_0: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst1_map {
        actions = {
            inst1_set_hop_latency();
            NoAction;
        }
        key = {
            hdr.int_header.inst_1: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst2_map {
        actions = {
            inst2_set_q_info();
            NoAction;
        }
        key = {
            hdr.int_header.inst_2: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst3map {
        actions = {
            inst3_set_ingress_tstamp();
            NoAction;
        }
        key = {
            hdr.int_header.inst_3: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    apply {
        if(hdr.int_header.isValid()) {
            inst0_map.apply();
            inst1_map.apply();
            inst2_map.apply();
            inst3map.apply();
        }
    }          
}*/

control Int_data_update(inout headers hdr,inout standard_metadata_t standard_metadata, inout metadata meta) {
    
    //Int_inst_insert() int_inst_insert;   
    action int_add_hop_cnt() {
        hdr.int_header.total_hop_cnt = hdr.int_header.total_hop_cnt + 1;
    }
    action max_cnt() {
        hdr.int_header.e = 1;
    }
    action ipv4_update() {
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + (bit<16>) hdr.int_header.ins_cnt << 2;
    }
    action shim_update() {
        hdr.int_shim.len = hdr.int_shim.len + (bit<8>) hdr.int_header.ins_cnt;
    } 
    apply{
        if(hdr.int_header.max_hop_cnt != hdr.int_header.total_hop_cnt && hdr.int_header.e == 0) {
            int_add_hop_cnt();
            //int_inst_insert.apply(hdr,standard_metadata,meta);
            ipv4_update(); 
            shim_update();
        } 
        else {
            max_cnt();
        }
    }                  
}
    
control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action _drop() {
        mark_to_drop();
    }
    action set_nhop(bit<32> nhop_ipv4, bit<9> port) {
        meta.ingress_metadata.nhop_ipv4 = nhop_ipv4;
        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    action set_dmac(bit<48> dmac) {
        hdr.ethernet.dstAddr = dmac;
    }
    table ipv4_lpm {
        actions = {
            _drop;
            set_nhop;
            NoAction;
        }
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        size = 1024;
        default_action = NoAction();
    }
    table forward {
        actions = {
            set_dmac;
            _drop;
            NoAction;
        }
        key = {
            meta.ingress_metadata.nhop_ipv4: exact;
        }
        size = 512;
        default_action = NoAction();
    }
    apply {
        if (hdr.ipv4.isValid()) {
          ipv4_lpm.apply();
          forward.apply();
        }
    }
}

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    Int_data_update() int_data_update;
    action rewrite_mac(bit<48> smac) {
        hdr.ethernet.srcAddr = smac;
    }
    action _drop() {
        mark_to_drop();
    }
    action inst0_set_switch_id(bit<32> switch_id) {
        hdr.int_switch_id.setValid();
        hdr.int_switch_id.switch_id = switch_id;
    }
    action inst1_set_hop_latency() {
        hdr.int_hop_latency.setValid();
        hdr.int_hop_latency.hop_latency = (bit<32>) standard_metadata.deq_timedelta;
    }
    action inst2_set_q_info() {
        hdr.int_q_info.setValid();
        hdr.int_q_info.q_time = (bit<24>) standard_metadata.enq_timestamp;        
        hdr.int_q_info.q_length = (bit<8>) standard_metadata.enq_qdepth;
    }
    action inst3_set_ingress_tstamp() {
        hdr.int_ingress_tstamp.setValid();
        hdr.int_ingress_tstamp.ingress_tstamp = (bit<32>) standard_metadata.ingress_global_timestamp;
    }
    table send_frame {
        actions = {
            rewrite_mac;
            _drop;
            NoAction;
        }
        key = {
            standard_metadata.egress_port: exact;
        }
        size = 256;
        default_action = NoAction();
    }
    table inst0_map {
        actions = {
            inst0_set_switch_id;
            NoAction;
        }
        key = {
            hdr.int_header.inst_0: exact;
            hdr.ethernet.dstAddr: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst1_map {
        actions = {
            inst1_set_hop_latency;
            NoAction;
        }
        key = {
            hdr.int_header.inst_1: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst2_map {
        actions = {
            inst2_set_q_info;
            NoAction;
        }
        key = {
            hdr.int_header.inst_2: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    table inst3_map {
        actions = {
            inst3_set_ingress_tstamp;
            NoAction;
        }
        key = {
            hdr.int_header.inst_3: exact;
        }
        size = 256;
        default_action= NoAction();
    }
    apply {
        if (hdr.ipv4.isValid()) {
            send_frame.apply();
            if (hdr.int_shim.isValid()) {
                int_data_update.apply(hdr,standard_metadata,meta);
                if (hdr.int_header.e == 0) {
                    inst3_map.apply();
                    inst2_map.apply();
                    inst1_map.apply();
                    inst0_map.apply();
                }
            } 
        }
    }
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;
