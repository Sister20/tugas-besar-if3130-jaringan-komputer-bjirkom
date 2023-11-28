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
        self.broadcast_ip, self.broadcast_port, self.input_path = self.parser.get_args()
        self.connection = Connection(
            ip=self.broadcast_ip,
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
            f"[Handshake] [{address[0]}:{address[1]}] Initiating three way handshake with client "
        )
        print(f"[Handshake] [{address[0]}:{address[1]}] Sending SYN request to client")

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
            except TimeoutError:
                print(
                    f"[Error] Timeout Error while waiting for client {address[0]}:{address[1]} SYN-ACK response. Resending SYN request..."
                )

    def open_for_request(self):
        # the file size is soon to be change
        print(
            f"[!] Source file | {os.path.basename(self.input_path)} | {self.file_parser.get_size()} bytes\n"
        )

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

        n_segment = self.file_parser.get_count_segment() + 1
        sequence_base = 2
        sequence_max = sequence_base + WINDOW_SIZE + 1

        print(f"[!] [Client {address[0]}:{address[1]}] Initiating data transfer...")

        # ATTENTION uncomment for formulated checksum  error
        # formulated_checksum_error = 0
        while sequence_base - 2 < n_segment:
            
            # sending all file within window
            file_segments = self.parsefile_limit_window(sequence_base - 3)

            # ATTENTION uncomment for formulated checksum  error
            # formulated checksum  error
            # if formulated_checksum_error % 5 == 0:
            #     print("checksum altered")
            #     file_segments[0].set_checksum(9999)

            for i in range(WINDOW_SIZE):
                if sequence_base - 2 + i < n_segment:
                    print(
                        f"[Segment SEQ={sequence_base + i}] [Client {address[0]}:{address[1]}] Sending segment to client"
                    )

                    self.connection.sendMsg(file_segments[i].generate_bytes(), address)

            i = 0
            # ATTENTION uncomment for formulated checksum  error
            # formulated_checksum_error += 1
            while i < WINDOW_SIZE and sequence_base - 2 < n_segment:
                try:
                    reply_response, reply_address = self.connection.listenMsg()
                    if reply_address == address:
                        response = Segment()
                        response.parse_bytes(reply_response)

                        if (
                            response.get_flag().ack
                            and response.get_ack() == sequence_base
                        ):
                            sequence_base += 1
                            sequence_max += 1
                            print(
                                f"[Segment SEQ={response.get_seq()}] [Client {address[0]}:{address[1]}] [ACK] ACK Received, new sequence base = {sequence_base}"
                            )
                        elif not response.get_flag().ack:
                            print(
                                f"[Segment SEQ={sequence_base}] [Client {address[0]}:{address[1]}] [FLAG] Recieved Wrong Flag"
                            )
                        elif response.get_ack() < sequence_base:
                            print(
                                f"[Segment SEQ={sequence_base}] [Client {address[0]}:{address[1]}] [ACK] Not ACKED. Duplicate ACK found. Resending segment from sequence number {sequence_base}"
                            )
                            break
                        i += 1

                except:
                    print(
                        f"[Segment SEQ={sequence_base}] [Client {address[0]}:{address[1]}] [Timeout] ACK response timeout, resending segment from sequence number {sequence_base}"
                    )
                    break
        print(
            f"[!] [Client {address[0]}:{address[1]}] Data transfer finished. Initiate closing connection..."
        )

    def close_connection(self, address):
        """Closing connection with client

        Parameters
        ----------
        address : (str, int)
            Client address
        """
        # Sending FIN-ACK to client
        print(f"[Close] [Client {address[0]}:{address[1]}] Closing connection...")
        print(f"[Close] [Client {address[0]}:{address[1]}] Sending FIN-ACK to client")

        while True:
            self.segment = Flags.fin_ack(
                seq_num=100, ack_num=300
            )  # TODO: change the sequence number and ack num
            self.connection.sendMsg(self.segment.generate_bytes(), address)

            # Waiting for ACK response from client
            print(
                f"[Close] [Client {address[0]}:{address[1]}] Waiting client response..."
            )
            try:
                # Parse the response
                reply_segment, reply_address = self.connection.listenMsg()
                self.segment.parse_bytes(reply_segment)

                # Check if the response is appropriate
                if reply_address[1] == address[1]:
                    if self.segment.get_flag().ack:
                        print(
                            f"[Close] [Client {address[0]}:{address[1]}] Received ACK flag from client"
                        )
                        break
                    else:
                        print(
                            f"[Error] [Client {address[0]}:{address[1]}] Received invalid closing response from client"
                        )
                        exit()
                else:
                    print(
                        f"[Error] [Client {address[0]}:{address[1]}] Received from unknown address"
                    )
                    exit()

            except TimeoutError:
                # Resend if timeout
                print(
                    f"[Error] [Client {address[0]}:{address[1]}] Timeout Error while waiting for client ACK response. Resending FIN-ACK..."
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
                            f"[Close] [Client {address[0]}:{address[1]}] Received FIN-ACK flag from client"
                        )

                        # Sending ACK response to client
                        print(
                            f"[Close] [Client {address[0]}:{address[1]}] Sending ACK response to client"
                        )

                        # Sequence number ___ : ACK flag
                        self.segment = Flags.ack(
                            seq_num=101, ack_num=101
                        )  # TODO: change the sequence number and ack num
                        self.connection.sendMsg(self.segment.generate_bytes(), address)
                        break
                    else:
                        print(
                            f"[Error] [Client {address[0]}:{address[1]}] Received invalid closing response from client"
                        )
                        continue
                else:
                    print(
                        f"[Error] [Client {address[0]}:{address[1]}] Received from unknown address"
                    )
                    continue
            except TimeoutError:
                print(
                    f"[Error] [Client {address[0]}:{address[1]}] Timeout Error while waiting for client FIN-ACK request. Froce closing..."
                )
                break

        print(
            f"[Close] [Client {address[0]}:{address[1]}] Connection closed with client {address[0]}:{address[1]}"
        )

    def initiate_send_data(self):
        self.parsefile_to_segments()
        for client_address in self.client_list:
            self.three_way_handshake(client_address)
            self.send_data(client_address)
            self.close_connection(client_address)

    # -1 = meta include
    # > -1 = file only
    def parsefile_limit_window(self, offset: int):
        file_segments: list[Segment] = []
        segments_size = min(WINDOW_SIZE, self.file_parser.get_count_segment())

        if offset == -1:
            name = self.file_parser.get_name()
            ext = self.file_parser.get_extension()
            size = str(self.file_parser.get_size())

            metadata = (
                name.encode()
                + ",".encode()
                + ext.encode()
                + ",".encode()
                + size.encode()
            )
            metadata_segment = Segment()
            metadata_segment.set_payload(metadata)

            metadata_segment.set_seq(2)
            metadata_segment.set_ack(0)

            file_segments.append(metadata_segment)
            segments_size = (
                segments_size
                if WINDOW_SIZE > self.file_parser.get_count_segment()
                else segments_size - 1
            )
            offset += 1

        for i in range(segments_size):
            segment = Segment()
            segment.set_payload(self.file_parser.get_chunk(offset + i))
            segment.set_seq(offset + i + 3)
            segment.set_ack(3)
            file_segments.append(segment)

        return file_segments

    def parsefile_to_segments(self):
        self.file_segments: list[Segment] = []

        name = self.file_parser.get_name()
        ext = self.file_parser.get_extension()
        size = str(self.file_parser.get_size())

        metadata = (
            name.encode() + ",".encode() + ext.encode() + ",".encode() + size.encode()
        )
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
    server.initiate_send_data()
    server.connection.closeSocket()
