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

Run POX contoller with the scrambling-ip component:
```
$ ln -s ~/sdn-lab/scrambling_ip.py ext/scrambling_ip.py
$ ./pox/pox.py log.level --DEBUG scrambling_ip
```

Test that it works properly:

In mininet console run:
```
mininet> xterm h1 h2 h3
```
Now we should see 4 terminals corresponding to the hosts.

In terminal h1, h2 and h3 run:
```
nc -u -l 12345
```
We should have 3 hosts listening on the UDP port 12345.

In terminal h4 run:
```
nc -u 10.0.0.3 12345
```
Now feel free to write down somthing and press Enter.
_Who is receiving messages?_

What if you try to run this (in h4):
```
Ctrl^C
nc -u 10.0.0.1 12345
```
Who receives it now?
