from lib.Connection import Connection
from lib.ServerParser import ServerParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import MAX_SEGMENT


class Server:
    def __init__(self):
        self.parser = ServerParser()
        self.broadcast_port, self.input_path = self.parser.get_args()
        self.connection = Connection(
            ip="127.0.0.1",
            port=self.broadcast_port,
            is_server=True,
        )
        self.segment = Segment()

    # TODO: Add timeout implementation
    def three_way_handshake(self):
        while True:
            print("[Handshake] Waiting for clients...")
            _, address = self.connection.listenMsg()
            print(f"[Handshake] Received SYN request from client {address}")
            print(f"[Handshake] Sending SYN-ACK response to {address}")
            self.segment = Flags.syn_ack(seq_num=300, ack_num=101)
            self.connection.sendMsg(self.segment.generate_bytes(), ("127.0.0.1", 50001))
            print("[Handshake] Waiting client response...")
            _, address = self.connection.listenMsg()
            print("[Handshake] Received ACK flag from client")
            break
        print("Connection established")


if __name__ == "__main__":
    server = Server()
    server.three_way_handshake()
    server.connection.closeSocket()
