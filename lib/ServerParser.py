import argparse


class ServerParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            "-bp", "--broadcast_port", type=int, help="Broadcast Port"
        )
        self.parser.add_argument("-ip", "--input_path", type=str, help="Input Path")

    # Returns tuple (broadcast_port, input_path)
    def get_args(self):
        args = self.parser.parse_args()
        return args.broadcast_port, args.input_path
