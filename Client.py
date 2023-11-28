from lib.Connection import Connection
from lib.ClientParser import ClientParser
from lib.FileParser import FileParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import *


class Client:
    def __init__(self):
        self.parser = ClientParser()
        self.client_ip, self.client_port, self.broadcast_ip, self.broadcast_port, self.output_path = self.parser.get_args()
        self.connection = Connection(
            ip=self.client_ip,
            port=self.client_port,
            is_server=False,
        )
        self.segment = Segment()

    def three_way_handshake(self):
        try:
            # Waiting for SYN flag from server
            address = (self.broadcast_ip, self.broadcast_port)
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
                else:
                    print(
                        f"[Handshake] Received from unknown address {reply_address[0]}:{reply_address[1]})."
                    )
        except TimeoutError:
            print(
                f"[Error] Timeout Error while waiting for server {address[0]}:{address[1]}. Exiting..."
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
                    f"[Error] Timeout Error while waiting for server {address[0]}:{address[1]}. Resending SYN-ACK..."
                )
                # Resending SYN-ACK
                self.segment = Flags.syn_ack(seq_num=1, ack_num=0)
                self.connection.sendMsg(self.segment.generate_bytes(), address)

    def send_request(self):
        self.connection.sendMsg(
            self.segment.generate_bytes(), (self.broadcast_ip, self.broadcast_port)
        )

    def close_connection(self, address, seq_num, ack_num):
        """Closing connection with server"""
        print(f"[Close] [Server {address[0]}:{address[1]}] Received FIN-ACK from server")

        # Sending ACK to server
        print(f"[Close] [Server {address[0]}:{address[1]}] Sending ACK to server")

        self.send_ack(seq_num, ack_num)

        timeout_counter = 0

        print(f"[Close] [Server {address[0]}:{address[1]}] Sending FIN-ACK to server")
        while True:
            self.segment = Flags.fin_ack(seq_num + 1, ack_num + 1)
            self.connection.sendMsg(self.segment.generate_bytes(), address)
            try:
                # Waiting for ACK from server
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # Check the request is appropriate
                if reply_address[1] == self.broadcast_port:
                    if self.segment.get_flag().ack:
                        print(
                            f"[Close] [Server {address[0]}:{address[1]}] Received ACK from server"
                        )
                        break
                    else:
                        # Wait for valid response
                        print(
                            f"[Close] [Server {address[0]}:{address[1]}] Received invalid closing response from server, waiting for another response..."
                        )
                else:
                    # Wait for valid response
                    print(
                        f"[Close] [Server {address[0]}:{address[1]}] Received from unknown address, waiting for another response..."
                    )
            except TimeoutError:
                print(
                    f"[Error] [Server {address[0]}:{address[1]}] Timeout Error while waiting for server. Resending FIN-ACK..."
                )
                timeout_counter += 1
                if (timeout_counter == 5):
                    print(f"[Error] [Server {address[0]}:{address[1]}] Timeout Error while waiting for server. Closing connection...")
                    break

        print(f"[Close] [Server {address[0]}:{address[1]}] Connection with server is closed")
        self.connection.closeSocket()

    def send_ack(self, seq_num, ack_number):
        response = Flags.ack(seq_num, ack_number)
        self.connection.sendMsg(response.generate_bytes(), (self.broadcast_ip, self.broadcast_port))        

    def receive_data(self):
        # Sequence number 2 : Metadata
        # Sequence number 3++ : Actual data
        file_parser = FileParser(self.output_path)
        request_number = 2
        while True:
            segment_in_byte, server_addr = self.connection.listenMsg(LISTEN_TIMEOUT)
            
            if server_addr[1] == self.broadcast_port:
                self.segment.parse_bytes(segment_in_byte)

                if self.segment.get_flag().fin and self.segment.get_flag().ack and self.segment.is_valid_checksum():
                    self.close_connection(server_addr, self.segment.get_seq(), self.segment.get_ack())
                    break            

                elif self.segment.get_seq() == request_number and self.segment.is_valid_checksum():
                    if request_number == 2:
                        # if it's metadata
                        request_number += 1
                        metadata = file_parser.parse_metadata(self.segment.get_payload())
                        print(f"[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] Received Filename: {metadata['name']}.{metadata['ext']}, File Size: {metadata['size']} bytes")
                        self.send_ack(self.segment.get_seq(), self.segment.get_seq())                

                    else: 
                        # parse payload and write to file   
                        request_number += 1
                        self.send_ack(self.segment.get_seq(), self.segment.get_seq())
                        print(f'[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] Received, Ack sent')

                        payload = self.segment.get_payload()
                        file_parser.write_to_buffer(payload)
                    
                elif self.segment.get_seq() < request_number:
                    # duplicate
                    # print(request_number)
                    if self.segment.get_ack() > 3:
                        print(f"[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] [Duplicate] Multiple duplicate segment detected, sending ACK")
                        self.send_ack(self.segment.get_seq(), self.segment.get_seq())

                    print(f"[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] [Duplicate] Duplicate segment detected")
                    

                elif self.segment.get_seq() > request_number and self.segment.is_valid_checksum():
                    # out of order
                    print(f"[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] [Out-of-order] Sending previous ACK")
                    self.send_ack(request_number - 1, request_number - 1)

                else:
                    # corrupt 
                    print(f"[Segment SEQ={self.segment.get_seq()}] [Server {server_addr[0]}:{server_addr[1]}] Checksum failed, sending previous ACK")
                    self.send_ack(request_number - 1, request_number - 1)                    
                    

              

if __name__ == "__main__":
    client = Client()
    client.send_request()
    client.three_way_handshake()
    client.receive_data()