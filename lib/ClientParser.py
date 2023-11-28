import argparse
import os

class ClientParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-cip", "--client_ip", type=str, help="Client IP")
        self.parser.add_argument("-cp", "--client_port", type=int, help="Client Port")
        self.parser.add_argument("-bip", "--broadcast_ip", type=str, help="Broadcast IP")
        self.parser.add_argument(
            "-bp", "--broadcast_port", type=int, help="Broadcast Port"
        )
        self.parser.add_argument("-op", "--output_path", type=str, help="Output Path")

    def validate_input(self, args):
        # check if input is valid
        if (not isinstance(args.broadcast_port, int)):
            print("[!] Broadcast port input is not valid. Exiting...")
            exit()

        if (not isinstance(args.broadcast_ip, str)):
            print("[!] Broadcast ip input is not valid. Exiting...")
            exit()

        if (not isinstance(args.client_port, int)):
            print("[!] Client port input is not valid. Exiting...")
            exit()

        if (not isinstance(args.client_ip, str)):
            print("[!] Client ip input is not valid. Exiting...")
            exit()

        if (not isinstance(args.output_path, str)):
            print("[!] Input path is not valid. Exiting...")
            exit()
            
    # Returns tuple (client_port, broadcast_port, output_path)
    def get_args(self):
        args = self.parser.parse_args()
        self.validate_input(args)
        return args.client_ip, args.client_port, args.broadcast_ip, args.broadcast_port, args.output_path
