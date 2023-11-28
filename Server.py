from lib.Connection import Connection
from lib.ServerParser import ServerParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import LISTEN_TIMEOUT, WINDOW_SIZE, TIMEOUT
from lib.FileParser import FileParser
import threading 
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
        self.last_ack = 0
        self.last_seq = 0

    def ask_parallelization(self):
        choice = input(
            "[?] Do you want the server to enable paralelization? (y/n) "
        ).lower()

        while choice != 'y' and choice != 'n':
            print("[!] Please input correct input")
            choice = input("[?] Do you want the server to enable paralelization? (y/n) ").lower()

        if choice == "y":
            self.is_parallel = True
        else:
            self.is_parallel = False

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
                    print("[!] Please enter a correct input")
                    choice = input("[?] Listen more (y/n) ").lower()

                if choice == "n":
                    print("\nClient list:")
                    for idx, address in enumerate(self.client_list):
                        print(f"{idx+1}. {address[0]}:{address[1]}")
                    print("\n", end="")
                    break
                else:
                    print("[!] Listeing to more requests")

            except TimeoutError:
                print("[Error] Timeout Error when listening client. Exiting...")
                exit()

    def send_data(self, address):
        # Sequence number 2 : Metadata
        # Sequence number 3++ : Actual data

        n_segment = self.file_parser.get_count_segment() + 1
        sequence_base = 2
        sequence_max = sequence_base + WINDOW_SIZE + 1
        check_ack_lost = {"seq_num": 0, "times": 0}

        print(f"[!] [Client {address[0]}:{address[1]}] Initiating data transfer...")

        while sequence_base - 2 < n_segment:
            
            # sending all file within window
            file_segments = self.parsefile_limit_window(sequence_base - 3, check_ack_lost["times"])

            for i in range(WINDOW_SIZE):
                if sequence_base - 2 + i < n_segment:
                    print(
                        f"[Segment SEQ={sequence_base + i}] [Client {address[0]}:{address[1]}] Sending segment to client"
                    )
                    
                    self.connection.sendMsg(file_segments[i].generate_bytes(), address)
                    self.last_seq = file_segments[i].get_seq()

            i = 0
            while i < WINDOW_SIZE and sequence_base - 2 < n_segment:
                try:
                    reply_response, reply_address = self.connection.listenMsg()
                    if reply_address == address:
                        response = Segment()
                        response.parse_bytes(reply_response)

                        if not response.is_valid_checksum():
                            pass

                        elif (
                            response.get_flag().ack
                            and response.get_ack() == sequence_base
                        ):
                            self.last_ack = response.get_ack()
                            sequence_base = response.get_ack() + 1
                            sequence_max = sequence_base + WINDOW_SIZE + 1

                            if check_ack_lost['seq_num'] != 0:
                                check_ack_lost['seq_num'] = 0
                                check_ack_lost["times"] = 0
                            
                            print(
                                f"[Segment SEQ={response.get_ack()}] [Client {address[0]}:{address[1]}] [ACK] ACK Received, new sequence base = {sequence_base}"
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

                    if check_ack_lost['seq_num'] != sequence_base:
                        check_ack_lost['seq_num'] = sequence_base
                        check_ack_lost["times"] = 1
                    else:
                        check_ack_lost['times'] += 1
                    break
            
            # break if ack lost than 10 more times
            if check_ack_lost['times'] >= 10:
                print(f"[Error] Timeout Error ACK lost more than 10 times")
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
        timeout_counter = 0
        while True:
            self.last_seq += 1
            self.last_ack += 1
            self.segment = Flags.fin_ack(
                seq_num=self.last_seq, ack_num=self.last_ack
            )
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
                else:
                    print(
                        f"[Error] [Client {address[0]}:{address[1]}] Received from unknown address"
                    )

            except TimeoutError:
                # Resend if timeout
                print(
                    f"[Error] [Client {address[0]}:{address[1]}] Timeout Error while waiting for client ACK response. Resending FIN-ACK..."
                )
                timeout_counter += 1
                if timeout_counter >= 5:
                    break
        
        timeout_counter = 0
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
                        )
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
                    f"[Error] [Client {address[0]}:{address[1]}] Timeout Error while waiting for client FIN-ACK request. Resending ACK..."
                )
                timeout_counter += 1
                if timeout_counter >= 5:
                    print(f"[Error] Timeout Error more than 5 times. Closing connection...")
                    break

        print(
            f"[Close] [Client {address[0]}:{address[1]}] Connection closed with client {address[0]}:{address[1]}"
        )

    def establish_send_close_connection(self, address):
        self.three_way_handshake(address)
        self.send_data(address)
        self.close_connection(address)

    def initiate_send_data(self):
        if self.is_parallel:
            while True:
                _, client_address = self.connection_parallel.listenMsg(LISTEN_TIMEOUT)
                if client_address not in self.client_list:
                    self.client_list.append(client_address)
                    threading.Thread(target=self.establish_send_close_connection, args=(client_address,)).start()
        else:
            for client_address in self.client_list:
                self.establish_send_close_connection(client_address)


    # -1 = meta include
    # > -1 = file only
    def parsefile_limit_window(self, offset: int, ack: int):
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
            metadata_segment.set_ack(ack)

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
            segment.set_ack(ack)
            file_segments.append(segment)

        return file_segments

if __name__ == "__main__":
    server = Server()
    server.ask_parallelization()
    if not server.is_parallel: 
        server.open_for_request()
    server.initiate_send_data()
    server.connection.closeSocket()
