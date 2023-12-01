import argparse
import os

class ServerParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-bip", "--broadcast_ip", type=str, help="Broadcast IP")
        self.parser.add_argument(
            "-bp", "--broadcast_port", type=int, help="Broadcast Port"
        )
        self.parser.add_argument("-ip", "--input_path", type=str, help="Input Path")

    def validate_input(self, args):
        # check if input is valid
        if (not isinstance(args.broadcast_ip, str)):
            print("[!] Broadcast ip input is not valid. Exiting...")
            exit()

        if (not isinstance(args.broadcast_port, int)):
            print("[!] Broadcast port input is not valid. Exiting...")
            exit()

        if (not isinstance(args.input_path, str)):
            print("[!] Input path is not valid. Exiting...")
            exit()
        
        # if file not exists
        if not os.path.exists(args.input_path):
            print("[!] File does not exist. Exiting...")
            exit()    

    # Returns tuple (broadcast_port, input_path)
    def get_args(self):
        args = self.parser.parse_args()
        self.validate_input(args)
        return args.broadcast_ip, args.broadcast_port, args.input_path
