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

    def three_way_handshake(self):
        try: 
            # Waiting for SYN flag from server
            address = ("127.0.0.1", self.broadcast_port)
            print("[Handshake] Waiting for server...")

            while True:
                reply_segment, reply_address = self.connection.listenMsg(QUEUE_TIMEOUT)
                self.segment.parse_bytes(reply_segment)

                # If the response is appropriate
                if reply_address[1] == self.broadcast_port:
                    if self.segment.get_flag().syn:
                        print(f"[Handshake] Received SYN request from server {address[0]}:{address[1]}")
                        
                        # Sending SYN-ACK response to server
                        print(f"[Handshake] Sending SYN-ACK response to server {address[0]}:{address[1]}")
                        self.segment = Flags.syn_ack(seq_num=1, ack_num=0)
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
                    
                        # Waiting for ACK response from server
                        print("[Handshake] Waiting server response...")

                        while True:
                            reply_segment, reply_address = self.connection.listenMsg()
                            self.segment.parse_bytes(reply_segment)

                            if reply_address[1] == self.broadcast_port:
                                if self.segment.get_flag().ack and self.segment.get_ack == 1:
                                    print("[Handshake] Received ACK flag from server")
                                    print(f"[Handshake] Connection established with server {address[0]}:{address[1]}")
                                else:
                                    print(f"[Handshake] Received invalid handshake response from client {reply_address[0]}:{reply_address[1]})")
                                    exit()
                                break
                    else:
                        print(f"[Handshake] Received invalid handshake response from client {reply_address[0]}:{reply_address[1]})")
                        exit()
    
        except TimeoutError:
            print(f"[Error] Timeout Error while waiting for server 127.0.0.1:{self.broadcast_port}. Exiting...")
    
    def send_request(self):
        self.connection.sendMsg(self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port))

if __name__ == "__main__":
    client = Client()
    client.send_request()
    client.three_way_handshake()
    client.connection.closeSocket()
