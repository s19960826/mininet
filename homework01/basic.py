from pox.core import core
from pox.lib.revent import *
import pox.openflow.libopenflow_01 as of

class Basic(EventMixin):

    def __init__(self):
        if core.hasComponent("openflow"):
            self.listenTo(core.openflow)
        else:
            self.listenTo(core)

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
        switch = event.dpid
        packet = event.parsed
        print("PacketIn: " + str(packet))

        action = of.ofp_action_output(port=of.OFPP_ALL)

        # Flood the packet by installing a rule using a FlowMod message
        match = of.ofp_match.from_packet(packet)
        match.in_port = event.port
        flow = of.ofp_flow_mod(match=match)
        flow.idle_timeout = of.OFP_FLOW_PERMANENT
        flow.hard_timeout = of.OFP_FLOW_PERMANENT
        flow.priority = 65535
        flow.actions.append(action)
        if event.ofp.buffer_id != -1: 
            flow.buffer_id = event.ofp.buffer_id            
        event.connection.send(flow)

        # Flood the packet directly by sending a PacketOut message
        # msg = of.ofp_packet_out(action=action)
        # if event.ofp.buffer_id == -1: 
        #     msg.data = packet.pack()
        # else:
        #     msg.buffer_id = event.ofp.buffer_id
        # msg.in_port = event.port
        # event.connection.send(msg)
        return

def launch():
    core.registerNew(Basic)
