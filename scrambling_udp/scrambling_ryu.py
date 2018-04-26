from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp
from ryu import cfg


class L2Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)

        cfg.CONF.register_opts([
            cfg.IntOpt('udp_port', default=12345, help=('udp port'))
        ])
        self.ips_dict = {
            '10.0.0.1':
                ('10.0.0.2', '00:00:00:00:00:02'),
            '10.0.0.2':
                ('10.0.0.3', '00:00:00:00:00:03'),
            '10.0.0.3':
                ('10.0.0.1', '00:00:00:00:00:01')
        }

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        ofp_parser = dp.ofproto_parser
        pkt = packet.Packet(msg.data)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)
        if udp_pkt and udp_pkt.dst_port == cfg.CONF.udp_port:
            actions = []
            actions.append(ofp_parser.OFPActionSetDlDst(
                 self.ips_dict[ip_pkt.dst][1]))
            actions.append(ofp_parser.OFPActionSetNwDst(
                self.ips_dict[ip_pkt.dst][0]))
            actions.append(ofp_parser.OFPActionOutput(port=ofp.OFPP_FLOOD))
            out = ofp_parser.OFPPacketOut(
                datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
                actions=actions, data=msg.data)
            dp.send_msg(out)
        else:
            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]
            out = ofp_parser.OFPPacketOut(
                datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
                actions=actions, data=msg.data)
            dp.send_msg(out)
