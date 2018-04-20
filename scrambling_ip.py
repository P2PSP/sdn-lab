"""
This component redirect the IP packet sent to an IP host
to another different one. Doing that the sender doesn't
know the actual destination of the packet.

Note: IPs are static for this experiment.

Run mininet as follows:

sudo mn --topo single,4 --mac --switch ovsk --controller remote

"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr

log = core.getLogger()


class ScramblingPing (object):

    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.ips_dict = {
            IPAddr('10.0.0.1'):
                (IPAddr('10.0.0.4'), EthAddr('00:00:00:00:00:04')),
            IPAddr('10.0.0.2'):
                (IPAddr('10.0.0.3'), EthAddr('00:00:00:00:00:03')),
            IPAddr('10.0.0.3'):
                (IPAddr('10.0.0.2'), EthAddr('00:00:00:00:00:02')),
            IPAddr('10.0.0.4'):
                (IPAddr('10.0.0.1'), EthAddr('00:00:00:00:00:01'))
        }

    def _handle_PacketIn(self, event):
        inport = event.port
        packet = event.parsed

        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        ipp = packet.find('ipv4')
        if ipp:
            actions = []
            actions.append(of.ofp_action_dl_addr.set_dst(
                 self.ips_dict[ipp.dstip][1]))
            actions.append(of.ofp_action_nw_addr.set_dst(
                self.ips_dict[ipp.dstip][0]))
            actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            match = of.ofp_match.from_packet(packet, inport)

            msg = of.ofp_flow_mod(command=of.OFPFC_ADD, idle_timeout=10,
                                  hard_timeout=30, data=event.ofp,
                                  actions=actions, match=match)
            self.connection.send(msg)
        else:
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            action = of.ofp_action_output(port=of.OFPP_FLOOD)
            msg.actions.append(action)
            self.connection.send(msg)


def launch():
    def start(event):
        log.debug("Controlling %s" % (event.connection,))
        ScramblingPing(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start)
