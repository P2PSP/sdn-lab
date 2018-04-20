# SDN-LAB
Some experiments with SDN.

## Requirements
Install Mininet together with Open vSwitch, OpenFlow wireshark dissector and POX:

```
$ git clone git://github.com/mininet/mininet
$ mininet/util/install.sh -a
```

## Experiments

### scrambling-ping (as a POX component)

Run a network with one switch and 4 hosts:
```
$ sudo mn --topo single,4 --mac --switch ovsk --controller remote
```

Run POX contoller with the scrambling-ping component:
```
$ ln -s ~/sdn-lab/scrambling_ping.py ext/scrambling_ping.py
$ ./pox/pox.py log.level --DEBUG scrambling_ping
```