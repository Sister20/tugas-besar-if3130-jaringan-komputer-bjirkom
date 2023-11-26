from lib.Connection import Connection
from lib.ServerParser import ServerParser
from lib.Segment import Segment
from lib.flags import Flags
from lib.constant import MAX_SEGMENT, TIMEOUT_SERVER
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
    
    def open_for_request(self):
        # the file size is soon to be change 
        print(f"[!] Source file | {os.path.basename(self.input_path)} | {999} bytes\n")

        more_request = True
        while more_request:
            try: 
                _, address = self.connection.listenMsg(TIMEOUT_SERVER)
                self.client_list.append(address)
                print(f"[!] Received request from {address[0]}:{address[1]}")
                
                choice = input("[?] Listen more (y/n) ").lower()

                while choice != 'n' and choice != 'y':
                    choice = input("[?] Listen more (y/n) ").lower()
                    
                if choice == "n":
                    print("\nClient list:")
                    for idx, address in enumerate(self.client_list):
                        print(f"{idx+1}. {address[0]}:{address[1]}")
                    print("\n", end="")
                    break
            
            except TimeoutError:
                    print("[!] Timeout Error when listening client. Exiting...")
                    exit()
        
if __name__ == "__main__":
    server = Server()
    server.open_for_request()
    # server.three_way_handshake()
    server.connection.closeSocket()
