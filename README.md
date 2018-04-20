# SDN-LAB
Some experiments with SDN.

## Requirements
Install Mininet together with Open vSwitch, OpenFlow wireshark dissector and POX:

```
$ git clone git://github.com/mininet/mininet
$ mininet/util/install.sh -a
```

## Experiments

### scrambling-ip (as a POX component)
#### Runing it
Run a network with one switch and 4 hosts:
```
$ sudo mn --topo single,4 --mac --switch ovsk --controller remote
```

Run POX contoller with the scrambling-ip component:
```
$ ln -s ~/sdn-lab/scrambling_ip.py ext/scrambling_ip.py
$ ./pox/pox.py log.level --DEBUG scrambling_ip
```

#### Testing that it works properly

In mininet console run:
```
mininet> xterm h1 h2 h3
```
Now we should see 3 terminals that corresponds to the hosts 1, 2 and 3.

Check which IP has each host running:
```
ifconfig
```
We should have IPs assigned as follows:

Host |  IP
h1   |  10.0.0.1
h2   |  10.0.0.2
h3   |  10.0.0.3

In terminals h1, h2 and h3 (in each one) run:
```
nc -u -l 12345
```
We should have 3 hosts listening on the UDP port 12345. We use netcat to achieve it.

In terminal h4 run:
```
nc -u 10.0.0.3 12345
```
Now you we have a netcat client running on h4. Now feel free to write down somthing and press Enter.

- _Who is receiving messages?_
- _Is it the peer which IP=10.0.0.3? Sure?_

What if you try to run this (in h4):
```
Ctrl^C
nc -u 10.0.0.1 12345
```
- _Who receives it now?_
