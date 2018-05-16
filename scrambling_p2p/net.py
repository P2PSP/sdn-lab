#!/usr/bin/python

import sys
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, OVSSwitch


class MinimalTopo(Topo):
    "Minimal topology with a single switch and two hosts"

    def build(self, hosts=9):
        # Create a switch
        s1 = self.addSwitch('s1')

        # Create two hosts.
        for h in range(0, hosts):
            self.addLink(s1, self.addHost('h%s' % (h + 1)))


def runMinimalTopo(team_size):
    "Bootstrap a Mininet network using the Minimal Topology"

    # Create an instance of our topology
    hosts = team_size + 1
    topo = MinimalTopo(hosts)

    # Create a network based on the topology using OVS and controlled by
    # a remote controller.
    net = Mininet(
        topo=topo,
        controller=lambda name: RemoteController(name, ip='127.0.0.1'),
        switch=OVSSwitch,
        autoSetMacs=True)

    # Actually start the network
    net.start()

    for host in net.hosts[:-3]:
        host.cmd('python3 dummy_hp.py -p 12345 -s 10.0.0.' +
                 str(hosts) + ' -z 8&')

    net.hosts[-3].cmd('python3 dummy_tp.py -p 12345 -s 10.0.0.' +
                      str(hosts) + ' -z 8&')
    net.hosts[-2].cmd('python3 dummy_mp.py -p 12345 -s 10.0.0.' +
                      str(hosts) + ' -z 8 -t 5&')
    results = net.hosts[-1].cmd('python3 dummy_s.py -p 12345 -z 8')
    print(results)
    # Drop the user in to a CLI so user can run commands.
    # CLI(net)

    # After the user exits the CLI, shutdown the network.
    net.stop()


if __name__ == '__main__':
    # This runs if this file is executed directly
    setLogLevel('info')
    team_size = int(sys.argv[1])
    runMinimalTopo(team_size)

# Allows the file to be imported using `mn --custom <filename> --topo minimal`
topos = {
    'min': MinimalTopo
}
