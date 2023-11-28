from lib.Connection import Connection
from lib.ServerParser import ServerParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import MAX_SEGMENT, LISTEN_TIMEOUT, WINDOW_SIZE
from lib.FileParser import FileParser
import os


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
        self.client_list = list()

        self.file_parser = FileParser(self.input_path, True)

    # TODO: Resend if timeout
    def three_way_handshake(self, address):
        # Sending SYN requests to client
        print(
            f"[Handshake] Initiating three way handshake with client {address[0]}:{address[1]}"
        )
        print(f"[Handshake] Sending SYN request to client {address[0]}:{address[1]}")

        while True:
            # Sequence number 0 : SYN flag
            self.segment = Flags.syn(seq_num=0)
            self.connection.sendMsg(self.segment.generate_bytes(), address)

            try:
                # Waiting for response
                print("[Handshake] Waiting client response...")
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # If the response is appropriate
                if reply_address[1] == address[1]:
                    if self.segment.get_flag().syn and self.segment.get_flag().ack:
                        print(
                            f"[Handshake] Received SYN-ACK response from client {address[0]}:{address[1]}"
                        )

                        # Send ack to address
                        print(
                            f"[Handshake] Sending ACK response to client {address[0]}:{address[1]}"
                        )

                        # Sequence number 1 : ACK flag
                        self.segment = Flags.ack(seq_num=1, ack_num=1)
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
                        print(
                            f"[Handshake] Connection established with client {address[0]}:{address[1]}"
                        )
                        break
                    else:
                        print(
                            f"[Error] Received invalid handshake response from client {reply_address[0]}:{reply_address[1]}"
                        )
                        exit()
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for client {address[0]}:{address[1]} SYN-ACK response. Resending SYN request..."
                )

    def open_for_request(self):
        # the file size is soon to be change
        print(f"[!] Source file | {os.path.basename(self.input_path)} | {999} bytes\n")

        more_request = True
        while more_request:
            try:
                _, address = self.connection.listenMsg(LISTEN_TIMEOUT)
                self.client_list.append(address)
                print(f"[!] Received request from {address[0]}:{address[1]}")

                choice = input("[?] Listen more (y/n) ").lower()

                while choice != "n" and choice != "y":
                    choice = input("[?] Listen more (y/n) ").lower()

                if choice == "n":
                    print("\nClient list:")
                    for idx, address in enumerate(self.client_list):
                        print(f"{idx+1}. {address[0]}:{address[1]}")
                    print("\n", end="")
                    break

            except TimeoutError:
                print("[Error] Timeout Error when listening client. Exiting...")
                exit()

    def send_data(self, address):
        # Sequence number 2 : Metadata
        # Sequence number 3++ : Actual data

        n_segment = len(self.segment_list)
        sequence_base = 2
        sequence_max = sequence_base + WINDOW_SIZE + 1

        print(f"[!] [Client {address[0]}:{address[1]}] Initiating data transfer...")

        while sequence_base < n_segment:
            # sending all file within window
            for i in range(WINDOW_SIZE + 1):
                if sequence_base + i < n_segment:
                    print(
                        f"[!] [Client {address[0]}:{address[1]}] [Num={sequence_base + i}] Sending segment to client"
                    )

                    # TODO: Check if the segmet list is the right variable
                    self.connection.sendMsg(
                        self.segment_list[sequence_base + i].generate_bytes(), address
                    )

            for i in range(WINDOW_SIZE + 1):
                try:
                    while True:
                        reply_response, reply_address = self.connection.listenMsg()
                        if reply_address == address:
                            response = Segment()
                            response.parse_bytes(reply_response)

                            if (
                                response.get_flag().ack
                                and response.get_seq() == sequence_base
                            ):
                                sequence_base += 1
                                sequence_max += 1
                                print(
                                    f"[!] [Client {address[0]}:{address[1]}] [ACK] ACK Received, new sequence base = {sequence_base}"
                                )
                            elif not response.get_flag().ack:
                                print(
                                    f"[!] [Client {address[0]}:{address[1]}] [FLAG] Recieved Wrong Flag"
                                )
                            else:
                                print(
                                    f"[!] [Client {address[0]}:{address[1]}] [ACK] Recieved Wrong ACK"
                                )

                except:
                    print(
                        f"[!] [Client {address[0]}:{address[1]}] [Timeout] ACK response timeout, resending sequence number {sequence_base}"
                    )

    def close_connection(self, address):
        """Closing connection with client

        Parameters
        ----------
        address : (str, int)
            Client address
        """
        # Sending FIN-ACK to client
        print("[Close] Closing connection...")
        print(f"[Close] Sending FIN-ACK to client {address[0]}:{address[1]}")

        while True:
            self.segment = Flags.fin_ack(
                seq_num=100, ack_num=300
            )  # TODO: change the sequence number and ack num
            self.connection.sendMsg(self.segment.generate_bytes(), address)

            # Waiting for ACK response from client
            print("[Close] Waiting client response...")
            try:
                # Parse the response
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # Check if the response is appropriate
                if reply_address[1] == address[1]:
                    if self.segment.get_flag().ack:
                        print(
                            f"[Close] Received ACK flag from client {address[0]}:{address[1]}"
                        )
                        break
                    else:
                        print(
                            f"[Error] Received invalid closing response from client {reply_address[0]}:{reply_address[1]}"
                        )
                        exit()
                else:
                    print(
                        f"[Error] Received from unknown address {reply_address[0]}:{reply_address[1]}"
                    )
                    exit()

            except TimeoutError:
                # Resend if timeout
                print(
                    f"[Error] Timeout Error while waiting for client {address[0]}:{address[1]} ACK response. Resending FIN-ACK..."
                )

        # Waiting for FIN-ACK request from client
        while True:
            try:
                # Parse the request
                req_segment, req_address = self.connection.listenMsg()
                self.segment.parse_bytes(req_segment)

                # Check if the request is appropriate
                if req_address[1] == address[1]:
                    if self.segment.get_flag().fin and self.segment.get_flag().ack:
                        print(
                            f"[Close] Received FIN-ACK flag from client {address[0]}:{address[1]}"
                        )

                        # Sending ACK response to client
                        print(
                            f"[Close] Sending ACK response to client {address[0]}:{address[1]}"
                        )

                        # Sequence number ___ : ACK flag
                        self.segment = Flags.ack(
                            seq_num=101, ack_num=101
                        )  # TODO: change the sequence number and ack num
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
                        break
                    else:
                        print(
                            f"[Error] Received invalid closing response from client {req_address[0]}:{req_address[1]}"
                        )
                        continue
                else:
                    print(
                        f"[Error] Received from unknown address {req_address[0]}:{req_address[1]}"
                    )
                    continue
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for client {address[0]}:{address[1]} FIN-ACK request. Exiting..."
                )
                exit()

        self.connection.closeSocket()
        print(f"[Close] Connection closed with client {address[0]}:{address[1]}")

    def initiate_send_data(self):
        for client_address in self.client_list:
            self.three_way_handshake(client_address)
            self.file_transfer(client_address)
    
    def parsefile_to_segments(self):
        self.file_segments: list[Segment] = []

        name = self.file_parser.get_name()
        ext = self.file_parser.get_extension()
        size = str(self.file_parser.get_size())

        metadata = name.encode() + ",".encode() + ext.encode() + ",".encode() + size.encode()
        metadata_segment = Segment()
        metadata_segment.set_payload(metadata)

        metadata_segment.set_seq(2)
        metadata_segment.set_ack(0)

        self.file_segments.append(metadata_segment)

        num_segment = self.file_parser.get_count_segment()

        for i in range(num_segment):
            segment = Segment()
            segment.set_payload(self.file_parser.get_chunk(i))
            segment.set_seq(i + 3)
            segment.set_ack(3)
            self.file_segments.append(segment)

if __name__ == "__main__":
    server = Server()
    server.open_for_request()
    server.three_way_handshake(("127.0.0.1", 3001))
    # server.connection.closeSocket()
    server.close_connection(("127.0.0.1", 3001))
