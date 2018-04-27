from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp
from ryu import cfg
from random import sample


class ScramblingP2P(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ScramblingP2P, self).__init__(*args, **kwargs)

        cfg.CONF.register_opts([
            cfg.ListOpt('peers_list', default=None, help=('List of peers'))
        ])
        self.peers_list = []
        for address in cfg.CONF.peers_list:
            self.peers_list.append(
                (address.split(":")[0], int(address.split(":")[1]))
            )
        print(self.peers_list)
        # self.mac_to_port = {}
        self.scrambling_list = dict(
            zip(self.peers_list, sample(self.peers_list, len(self.peers_list)))
        )
        print(self.scrambling_list)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)

        if udp_pkt:
            dst_peer = (ip_pkt.dst, udp_pkt.dst_port)
            if dst_peer in self.scrambling_list:
                match = dp.ofproto_parser.OFPMatch(in_port=msg.in_port)
                actions = []
                actions.append(ofp_parser.OFPActionSetDlDst(
                    'ff:ff:ff:ff:ff:ff'))
                actions.append(ofp_parser.OFPActionSetNwDst(
                    self.scrambling_list[dst_peer]))
                actions.append(ofp_parser.OFPActionOutput(port=ofp.OFPP_FLOOD))
                out = ofp_parser.OFPFlowMod(
                    datapath=dp, buffer_id=msg.buffer_id,
                    actions=actions, match=match, hard_timeout=30,
                    idle_timeout=10)
                dp.send_msg(out)
            else:
                actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        else:
            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=msg.data)
        dp.send_msg(out)
