# Running an experiment with HPs, a S, an MP and a TP
## Run Mininet
Run a network with one switch and 9 hosts:
```
$ sudo mn --topo single,9 --mac --switch ovsk --controller remote
```
## Run Ryu App
```
$ ryu-manager scrambling_p2p.py --config-file scrambling_p2p.conf
```

The configuration for this experiment is in the config file `scrambling_p2p.conf`
- Peers: 10.0.0.1, 10.0.0.0.2, 10.0.0.3, 10.0.0.0.4, 10.0.0.5, 10.0.0.0.6, 10.0.0.7, 10.0.0.0.8
- Splitter: 10.0.0.9
- UDP Port: 12345

## Testing that it works properly

In mininet console run a HP for peers 1 to 6:
```
mininet> h[n] python3 dummy_hp.py -p 12345 -s 10.0.0.9 -z 8
```
Where [n] is a number from 1 to 6.

Now run a TP in host 7:
```
mininet> h7 python3 dummy_tp.py -p 12345 -s 10.0.0.9 -z 8
```
Now a MP in host 8 choosing as a target of the attack host 5:
```
mininet> h8 python3 dummy_mp.py -p 12345 -s 10.0.0.9 -z 8 -t 5
```
Finally, run a S in host 9:
```
mininet> h9 python3 dummy_s.py -p 12345 -z 8
```
Is the attack detected? Who was being attacked when the TP detected it?