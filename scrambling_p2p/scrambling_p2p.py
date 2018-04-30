from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp
from ryu import cfg
from random import sample


class ScramblingP2P(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ScramblingP2P, self).__init__(*args, **kwargs)

        self.peers_list = []
        self.ip_to_mac = {}
        self.mac_to_port = {}
        cfg.CONF.register_opts([
            cfg.ListOpt('peers_list', default=None, help=('List of peers'))
        ])
        for address in cfg.CONF.peers_list:
            self.peers_list.append(
                (address.split(":")[0], int(address.split(":")[1]))
            )
        print("List of the team:\n{}".format(self.peers_list))
        # self.mac_to_port = {}
        self.scrambling_list = dict(
            zip(self.peers_list, sample(self.peers_list, len(self.peers_list)))
        )
        print("Scrambling List:\n{}".format(self.scrambling_list))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry. (OF 1.3+)
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        in_port = msg.match['in_port']
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)

        if udp_pkt and 1 == 0:
            dst_peer = (ip_pkt.dst, udp_pkt.dst_port)
            if dst_peer in self.scrambling_list:
                self.ip_to_mac[ip_pkt.src] = eth_pkt.src
                self.mac_to_port[eth_pkt.src] = msg.in_port
                if self.scrambling_list[dst_peer][0] in self.ip_to_mac:
                    dst_mac = self.ip_to_mac[
                        self.scrambling_list[dst_peer][0]
                    ]
                    dst_port = self.mac_to_port[dst_mac]
                else:
                    dst_mac = 'ff:ff:ff:ff:ff:ff'
                    dst_port = ofp.OFPP_FLOOD

                print("Message to", dst_peer, "from", ip_pkt.src)
                match = dp.ofproto_parser.OFPMatch(
                    in_port=msg.in_port,
                    nw_dst=dst_peer[0],
                    tp_dst=dst_peer[1])
                actions = []
                actions.append(ofp_parser.OFPActionSetDlDst(dst_mac))
                actions.append(ofp_parser.OFPActionSetNwDst(
                    self.scrambling_list[dst_peer][0]))
                actions.append(ofp_parser.OFPActionOutput(port=dst_port))
                # TO-DO: Use self.add_flow()
                out = ofp_parser.OFPFlowMod(
                    command=ofp.OFPFC_ADD,
                    datapath=dp, buffer_id=msg.buffer_id,
                    actions=actions, match=match, hard_timeout=30,
                    idle_timeout=10)
                dp.send_msg(out)
            else:
                actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        else:
            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=msg.data)
        dp.send_msg(out)
