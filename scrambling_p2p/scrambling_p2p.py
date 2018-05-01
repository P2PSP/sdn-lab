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
            print("Flow with no buffer_id")
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
            print("Flow with no buffer_id")
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

        if udp_pkt:
            dst_peer = (ip_pkt.dst, udp_pkt.dst_port)
            if dst_peer in self.scrambling_list:
                self.ip_to_mac[ip_pkt.src] = eth_pkt.src
                self.mac_to_port[eth_pkt.src] = in_port
                if self.scrambling_list[dst_peer][0] in self.ip_to_mac:
                    dst_ip = self.scrambling_list[dst_peer][0]
                    dst_mac = self.ip_to_mac[dst_ip]
                    dst_port = self.mac_to_port[dst_mac]
                else:
                    dst_ip = self.scrambling_list[dst_peer][0]
                    dst_mac = 'ff:ff:ff:ff:ff:ff'
                    dst_port = ofp.OFPP_FLOOD

                print("Message to", dst_peer, "from", ip_pkt.src, "sent to",
                      dst_ip, "via", dst_mac)
                match = dp.ofproto_parser.OFPMatch(
                    in_port=in_port, eth_type=0x800)
                # 0x800 => IPv4 type.
                # See more in https://en.wikipedia.org/wiki/EtherType
                actions = []
                actions.append(ofp_parser.OFPActionSetField(eth_dst=dst_mac))
                actions.append(ofp_parser.OFPActionSetField(ipv4_dst=dst_ip))
                actions.append(ofp_parser.OFPActionOutput(port=dst_port))
                # TO-DO: Use self.add_flow()
                if msg.buffer_id != ofp.OFP_NO_BUFFER:
                    self.add_flow(dp, 1, match, actions, msg.buffer_id)
                    return
                else:
                    self.add_flow(dp, 1, match, actions)
                '''
                inst = [ofp_parser.OFPInstructionActions(
                    ofp.OFPIT_APPLY_ACTIONS, actions)]
                out = ofp_parser.OFPFlowMod(
                    command=ofp.OFPFC_ADD,
                    datapath=dp, buffer_id=msg.buffer_id,
                    instructions=inst, match=match, hard_timeout=30,
                    idle_timeout=10)
                dp.send_msg(out)
                '''
            else:
                actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        else:
            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
        out = ofp_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=msg.data)
        dp.send_msg(out)
