from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import EthAddr

class Firewall(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)
        self.mac_to_port = {} # The hash table for the MAC address and port mapping
        self.mac_to_port[EthAddr('00:00:00:00:00:01')] = 1
        self.mac_to_port[EthAddr('00:00:00:00:00:02')] = 2
        self.mac_to_port[EthAddr('00:00:00:00:00:03')] = 3
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

        packet = event.parsed
        packet_in = event.ofp

        if packet_in.in_port != 2: # if the packet is not from h2
            msg = of.ofp_flow_mod()
            if packet.dst in self.mac_to_port: # if we already know the destination port
                action = of.ofp_action_output(port = self.mac_to_port[packet.dst])
                print("Install flow from Port " + str(packet_in.in_port) + " to Port " + str(self.mac_to_port[packet.dst]))
            else: # if we don't know the destination port, flood the packet
                action = of.ofp_action_output(port = of.OFPP_ALL)
                print("Don't know the destination port. Broadcast the packet.")
            msg.match = of.ofp_match.from_packet(packet)
            msg.data = packet_in
            msg.match.in_port = packet_in.in_port
            msg.idle_timeout = of.OFP_FLOW_PERMANENT
            msg.hard_timeout = of.OFP_FLOW_PERMANENT
            msg.priority = 65535
            if event.ofp.buffer_id != -1: 
                msg.buffer_id = event.ofp.buffer_id    
            msg.actions.append(action)
            event.connection.send(msg)
            
        else: # block the packet
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet)
            event.connection.send(msg)
            print("Flow from port 2. Blocked.")

def launch():
    core.registerNew(Firewall)
