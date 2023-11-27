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
                        print(
                            f"[Handshake] Received SYN request from server {address[0]}:{address[1]}"
                        )

                        # Sending SYN-ACK response to server
                        print(
                            f"[Handshake] Sending SYN-ACK response to server {address[0]}:{address[1]}"
                        )
                        self.segment = Flags.syn_ack(seq_num=1, ack_num=0)
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
                        break
                    else:
                        print(
                            f"[Handshake] Received invalid handshake response from client {reply_address[0]}:{reply_address[1]})."
                        )
                        # exit()
                else:
                    print(
                        f"[Handshake] Received from unknown address {reply_address[0]}:{reply_address[1]})."
                    )
                    # exit()
        except TimeoutError:
            print(
                f"[Error] Timeout Error while waiting for server {reply_address[0]}:{reply_address[1]}. Exiting..."
            )
            exit()

        # Waiting for ACK response from server
        print("[Handshake] Waiting server response...")

        while True:
            try:
                # Waiting for ACK response from server
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # Check if the response is appropriate
                if reply_address[1] == self.broadcast_port:
                    if self.segment.get_flag().ack and self.segment.get_ack() == 1:
                        print(
                            f"[Handshake] Received ACK flag from server {address[0]}:{address[1]}"
                        )
                        print(
                            f"[Handshake] Connection established with server {address[0]}:{address[1]}"
                        )
                        break
                    else:
                        print(
                            f"[Handshake] Received invalid handshake response from client {reply_address[0]}:{reply_address[1]}). Resending SYN-ACK..."
                        )
                        # Resending SYN-ACK
                        self.segment = Flags.syn_ack(seq_num=1, ack_num=0)
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for server {reply_address[0]}:{reply_address[1]}. Resending SYN-ACK..."
                )
                # Resending SYN-ACK
                self.segment = Flags.syn_ack(seq_num=1, ack_num=0)
                self.connection.sendMsg(self.segment.generate_bytes(), address)

    def send_request(self):
        self.connection.sendMsg(
            self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port)
        )

    def close_connection(self):
        """Closing connection with server"""
        print("[Close] Closing connection with server...")
        print("[Close] Waiting for FIN-ACK from server...")
        address = ("127.0.0.1", self.broadcast_port)
        while True:
            try:
                # Waiting for FIN-ACK from server
                req_segment, req_address = self.connection.listenMsg()
                self.segment.parse_bytes(req_segment)

                # Check the request is appropriate
                if req_address[1] == self.broadcast_port:
                    if self.segment.get_flag().fin and self.segment.get_flag().ack:
                        print(
                            f"[Close] Received FIN-ACK from server {req_address[0]}:{req_address[1]}"
                        )

                        # Sending ACK to server
                        print(
                            f"[Close] Sending ACK to server {req_address[0]}:{req_address[1]}"
                        )

                        self.segment = Flags.ack(
                            seq_num=300, ack_num=101
                        )  # TODO: change seq_num and ack_num
                        self.connection.sendMsg(
                            self.segment.generate_bytes(),
                            ("127.0.0.1", self.broadcast_port),
                        )
                        break
                    else:
                        # Wait for valid response
                        print(
                            f"[Close] Received invalid closing response from server {req_address[0]}:{req_address[1]}, waiting for another response..."
                        )
                else:
                    # Wait for valid response
                    print(
                        f"[Close] Received from unknown address {req_address[0]}:{req_address[1]}, waiting for another response..."
                    )
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for server {req_address[0]}:{req_address[1]}. Exiting..."
                )
                self.connection.closeSocket()
                exit()

        print(f"[Close] Sending FIN-ACK to server {address[0]}:{address[1]}")
        while True:
            self.segment = Flags.fin_ack(
                seq_num=300, ack_num=101
            )  # TODO: change seq_num and ack_num
            self.connection.sendMsg(
                self.segment.generate_bytes(), ("127.0.0.1", self.broadcast_port)
            )
            try:
                # Waiting for ACK from server
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # Check the request is appropriate
                if reply_address[1] == self.broadcast_port:
                    if self.segment.get_flag().ack:
                        print(
                            f"[Close] Received ACK from server {reply_address[0]}:{reply_address[1]}"
                        )
                        break
                    else:
                        # Wait for valid response
                        print(
                            f"[Close] Received invalid closing response from server {reply_address[0]}:{reply_address[1]}, waiting for another response..."
                        )
                else:
                    # Wait for valid response
                    print(
                        f"[Close] Received from unknown address {reply_address[0]}:{reply_address[1]}, waiting for another response..."
                    )
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for server {address[0]}:{address[1]}. Resending FIN-ACK..."
                )


if __name__ == "__main__":
    client = Client()
    client.send_request()
    client.three_way_handshake()
    # client.connection.closeSocket()
    client.close_connection()
