from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr,IPAddr

class Load_balancer(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        self.N = 30   # number of server
        self.ind = 0 # id of chosen sevcer
        self.request = 0 # have request or not
        self.cur_ser = -1 # current server 
        self.cur_client = -1 # current client
        self.dicts = {} 
    def _handle_ComponentRegistered(self, event):
        self.addListener(GoingDownEvent, _handle_GoingDownEvent)
        if event.name == "openflow":
            self.listenTo(core.openflow)
        else:
            pass
    
    # You should modify the handlers below.
    def _handle_ConnectionUp(self, event):
        pass

    def _handle_ConnectionDown(self, event):
        pass

    def _handle_FlowRemoved(self, event):
        pass

    def _handle_PortStatus(self,event):
        pass

    def _handle_FlowStatsReceived(self,event):
        pass

    def _handle_PacketIn(self, event):
        
        balancer_ip = IPAddr("10.0.0.99")
        balancer_eth = EthAddr("00:00:00:00:00:99")

        packet = event.parsed
        packet_in = event.ofp

        flow = of.ofp_flow_mod()
        flow.match = of.ofp_match.from_packet(packet)
        flow.match.in_port = packet_in.in_port
        if flow.match.nw_src not in self.dicts:
            self.dicts[flow.match.nw_src] = packet_in.in_port
        if flow.match.nw_dst == balancer_ip: # if the request is to balancer
            print("[Request]: From " + str(flow.match.nw_src) + " to " + str(flow.match.nw_dst))             
 
            if flow.match.in_port == self.ind+1: # if the chosen server is the same as the client
                self.ind = (self.ind + 1) % self.N # shift the server id
           
            ethnum = str(hex(self.ind+1)) 
            if self.ind < 15:
                ethnum = "0" + ethnum[2:len(ethnum)]
            else:
                ethnum = ethnum[2:len(ethnum)]
            ipnum = str(self.ind+1)

            server_port = self.ind+1
            server_ip = IPAddr("10.0.0." + ipnum)
            server_eth = EthAddr("00:00:00:00:00:" + ethnum)                 
            print("The chosen server is " + str(server_ip)) 
            print(server_eth)     

            flow.buffer_id = packet_in.buffer_id        

            new_ip_dst  = of.ofp_action_nw_addr(7,server_ip)
            new_eth_dst  = of.ofp_action_dl_addr(5,server_eth)
        

            action = of.ofp_action_output(port = server_port)
            flow.actions.append(new_ip_dst)
            flow.actions.append(new_eth_dst)
            self.ind = (self.ind + 1) %self.N
            
                    
            flow.idle_timeout = of.OFP_FLOW_PERMANENT
            flow.hard_timeout = of.OFP_FLOW_PERMANENT
            flow.priority = 65535

            flow.actions.append(action)
            event.connection.send(flow)
            flow.command = of.OFPFC_DELETE       
            event.connection.send(flow)
           
            # indicate the current server and client info
            self.cur_client = packet_in.in_port
            self.cur_ser = server_port
            self.request = 1
        else:
            if flow.match.nw_dst in self.dicts:
                outport = self.dicts[flow.match.nw_dst]
            else:
                outport = of.OFPP_ALL     
            if outport == self.cur_client and self.request == 1:   
                #response message

                new_ip_src = of.ofp_action_nw_addr(6,balancer_ip)
                new_eth_src = of.ofp_action_dl_addr(4,balancer_eth)

                action = of.ofp_action_output(port = outport)

                flow.buffer_id = packet_in.buffer_id           

                flow.idle_timeout = of.OFP_FLOW_PERMANENT
                flow.hard_timeout = of.OFP_FLOW_PERMANENT
                flow.priority = 65535
                
                flow.actions.append(new_ip_src)
                flow.actions.append(new_eth_src)
                flow.actions.append(action)
                event.connection.send(flow)
                flow.command = of.OFPFC_DELETE
                event.connection.send(flow)
   
                print("[Response]: Server " + str(self.cur_ser) + " response")

                self.cur_ser = -1
                self.cur_client = -1
                self.request = 0
 
            else:
                action = of.ofp_action_output(port = outport)
                flow.idle_timeout = of.OFP_FLOW_PERMANENT
                flow.hard_timeout = of.OFP_FLOW_PERMANENT
                flow.priority = 65535

                flow.actions.append(action)
                if event.ofp.buffer_id != -1: 
                    flow.buffer_id = event.ofp.buffer_id   
                event.connection.send(flow)
                print("Normal Message from " +  str(flow.match.nw_src) + " to " + str(flow.match.nw_dst))
                flow.command = of.OFPFC_DELETE
                event.connection.send(flow)
                
        
        return

def launch():
    core.registerNew(Load_balancer)
