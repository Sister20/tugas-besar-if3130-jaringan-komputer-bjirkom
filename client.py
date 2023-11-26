from lib.Connection import Connection
from lib.ClientParser import ClientParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import *


class Client:
    def __init__(self):
        self.parser = ClientParser()
        self.client_port, self.broadcast_port, self.output_path = self.parser.get_args()
        self.connection = Connection(
            ip="127.0.0.1",
            port=self.client_port,
            is_server=False,
        )
        self.segment = Segment()

    # TODO: Add timeout implementation
    def three_way_handshake(self):
        print("[Handshake] Initiating three way handshake...")
        while True:
            print(f"[Handshake] Sending SYN request to 127.0.0.1:{self.client_port}")
            self.segment = Flags.syn(seq_num=100)
            self.connection.sendMsg(
                self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port)
            )
            print("[Handshake] Waiting server response...")
            _, address = self.connection.listenMsg()
            print(f"[Handshake] Received SYN-ACK response from server {address}")
            print(f"[Handshake] Sending ACK response to {address}")
            self.segment = Flags.ack(seq_num=101, ack_num=301)
            self.connection.sendMsg(
                self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port)
            )
            break
        print("Connection established")

    def send_request(self):
        self.connection.sendMsg(self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port))

if __name__ == "__main__":
    client = Client()
    client.send_request()
    # client.three_way_handshake()
    client.connection.closeSocket()
