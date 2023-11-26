import argparse


class ClientParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-cp", "--client_port", type=int, help="Client Port")
        self.parser.add_argument(
            "-bp", "--broadcast_port", type=int, help="Broadcast Port"
        )
        self.parser.add_argument("-op", "--output_path", type=str, help="Output Path")

    # Returns tuple (client_port, broadcast_port, output_path)
    def get_args(self):
        args = self.parser.parse_args()
        return args.client_port, args.broadcast_port, args.output_path
