import socket
import argparse
import time

class DummyHP():

    def __init__(self, port, splitter, peer_list):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.splitter = splitter
        self.peer_list = peer_list

    def receive(self):
        data, address = self.sock.recvfrom(5)
        return (data.decode('utf8'), address)

    def send(self, data, address):
        self.sock.sendto(str(data).encode('utf8'), address)

    def run(self):
        while True:
            data, address = self.receive()
            print("{} received from {}".format(data, address))
            if data == "-9":
                exit()
            if address[0] == self.splitter:
                for p in self.peer_list:
                    self.send(data, p)
                    print("\t{} sent to {}".format(data, p))
                    time.sleep(0.05)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int,
                        help="UDP port used by peers")
    parser.add_argument("-s", "--splitter", type=str,
                        help="Splitter address")
    parser.add_argument("-z", "--size", type=int,
                        help="Team size (without splitter)")
    args = parser.parse_args()

    peer_list = []
    for p in range(1, args.size+1):
        peer_list.append(("10.0.0."+str(p), args.port))

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((args.splitter, 1))
    local_ip_address = s.getsockname()[0]

    print("Local IP {}".format(local_ip_address))
    peer_list.remove((local_ip_address, args.port))
    print("\nPeer List:{}".format(peer_list))
    peer = DummyHP(args.port, args.splitter, peer_list)
    peer.run()
