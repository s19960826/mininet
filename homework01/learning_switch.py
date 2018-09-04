from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of

class Learning_switch(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        self.mac_to_port = []
    def _handle_ComponentRegistered(self, event):
        self.addListener(GoingDownEvent, _handle_GoingDownEvent)
        if event.name == "openflow":
            self.listenTo(core.openflow)
        else:
            pass
        
    # You should modify the handlers below.
    def _handle_ConnectionUp(self, event):
        self.mac_to_port.append({}) # each switch have their own hash table

    def _handle_ConnectionDown(self, event):
        pass

    def _handle_FlowRemoved(self, event):
        pass

    def _handle_PortStatus(self,event):
        pass

    def _handle_FlowStatsReceived(self,event):
        pass

    def _handle_PacketIn(self, event):

        switch = event.dpid
        packet = event.parsed
        packet_in = event.ofp
        
        if packet.src not in self.mac_to_port[switch-1]:
            self.mac_to_port[switch-1][packet.src] = packet_in.in_port
        else:
           if self.mac_to_port[switch-1][packet.src] != packet_in.in_port:
               self.mac_to_port[switch-1][packet.src] = packet_in.in_port
         
        if packet.dst in self.mac_to_port[switch-1]:
            print("S" + str(switch) + ": Install flow from Port " + str(packet_in.in_port) + " to Port " + str(self.mac_to_port[switch-1][packet.dst]))
        
            msg = of.ofp_flow_mod()
            action = of.ofp_action_output(port = self.mac_to_port[switch-1][packet.dst])
            msg.match = of.ofp_match.from_packet(packet)
            msg.data = packet_in
            msg.match.in_port = packet_in.in_port
            msg.idle_timeout = of.OFP_FLOW_PERMANENT
            msg.hard_timeout = of.OFP_FLOW_PERMANENT
            msg.priority = 65535
            msg.actions.append(action)
            event.connection.send(msg)
        
        else:
            action = of.ofp_action_output(port = of.OFPP_ALL) 
            msg = of.ofp_packet_out()
            msg.data = packet_in

            msg.in_port = packet_in.in_port
            msg.actions.append(action)
            event.connection.send(msg)
            print("S" + str(switch) + ":destination port not exist. Broadcast the packet")


        return

def launch():
    core.registerNew(Learning_switch)
