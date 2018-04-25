# SDN-LAB
Some experiments with Software defined Networking (SDN).

## Requirements
Install Mininet together with Open vSwitch, OpenFlow wireshark dissector and POX:

```
$ git clone git://github.com/mininet/mininet
$ mininet/util/install.sh -a
```

## Experiments

### scrambling-ip (as a POX component)
This component redirect the IP packet sent to an IP host to another different one. Doing that the sender doesn't know the actual destination of the packet.

Note: IPs are static for this experiment, and it is limited to first three hosts.

See further instruction on [scrambling-ip](screambling-ip)

### scrambling-udp (as a POX component)
This component redirect the UDP packets sent to an specific port in any host to another different one. Doing that the sender doesn't know the actual destination of the packet.

Note: IPs and port are static for this experiment, and it is limited to first three hosts.

See further instruction on [scrambling-udp](screambling-udp)
