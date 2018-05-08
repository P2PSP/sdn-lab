import socket
import argparse
import time


class DummyS():

    def __init__(self, port, peer_list):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.peer_list = peer_list

    def send(self, data, address):
        self.sock.sendto(str(data), address)

    def run(self):
        data = 0
        while True:
            for p in self.peer_list:
                data += 1
                self.send(data, p)
                print("{} sent to {}".format(data, p))
                time.sleep(2)


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
