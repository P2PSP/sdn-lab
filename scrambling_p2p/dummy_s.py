import socket
import argparse
import time


class DummyS():

    def __init__(self, port, peer_list):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        self.sock.settimeout(1)
        self.peer_list = peer_list

    def receive(self):
        try:
            msg, address = self.sock.recvfrom(5)
        except socket.timeout:
            msg = b'0'
            address = ()
        return (msg.decode('utf8'), address)

    def send(self, data, address):
        self.sock.sendto(str(data).encode('utf8'), address)

    def run(self):
        data = 0
        _round = 0
        while True:
            _round += 1
            print("Round {}".format(_round))
            msg, address = self.receive()
            if int(msg) > 0:
                print("MP detected in round {} by {}".format(msg, address))
                exit()
            for p in self.peer_list:
                data += 1
                self.send(data, p)
                print("{} sent to {}".format(data, p))
                time.sleep(0.5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int,
                        help="UDP port used by peers")
    parser.add_argument("-z", "--size", type=int,
                        help="Team size (without splitter)")
    args = parser.parse_args()

    peer_list = []
    for p in range(1, args.size+1):
        peer_list.append(("10.0.0."+str(p), args.port))

    print("\nPeer List:{}".format(peer_list))
    peer = DummyS(args.port, peer_list)
    peer.run()
