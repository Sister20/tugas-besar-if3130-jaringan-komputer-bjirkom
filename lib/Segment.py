from SegmentFlag import SegmentFlag
from constant import *
from CRC import CRC
from struct import Struct

'''
    @attribute seq_num: int
    @attribute ack_num: int
    @attribute flag: SegmentFlag
    @attribute checksum: int
    @attribute payload: bytes
'''

class Segment:
    def __init__(self):
        self.seq_num: int = 0
        self.ack_num: int = 0
        self.flag: SegmentFlag = SegmentFlag(0b0)
        self.checksum: int = 0
        self.payload: bytes = b""

    def get_seq(self) -> int:
        return self.seq_num

    def get_ack(self) -> int:
        return self.ack_num

    def get_flag(self) -> SegmentFlag:
        return self.flag
    
    def get_payload(self) -> bytes:
        return self.payload

    def set_seq(self, seq_num: int):
        self.seq_num = seq_num

    def set_ack(self, ack_num: int):
        self.ack_num = ack_num

    def set_flag(self, flag: list[str]):
        _flag = 0b0
        for f in flag:
            if f == 'SYN':
                _flag |= SYN_FLAG
            elif f == 'ACK':
                _flag |= ACK_FLAG
            elif f == 'FIN':
                _flag |= FIN_FLAG
        self.flag = SegmentFlag(_flag)

    def set_checksum(self, checksum: int):
        self.checksum = checksum

    def set_payload(self, payload: bytes):
        self.payload = payload
        self.checksum = self.calculate_checksum()

    def calculate_checksum(self) -> int:
        checksum = CRC(self.payload)
        return checksum.calculate_reminder()

    def is_valid_checksum(self) -> bool:
        return self.calculate_checksum() == self.checksum

    def generate_bytes(self) -> bytes:
        segment = b""
        segment += Struct.pack("II", self.seq_num, self.ack_num)
        segment += self.flag.get_flag_bytes()
        segment += Struct.pack("x")
        segment += Struct.pack("H", self.checksum)
        segment += self.payload
        return segment
    
    def parse_bytes(self, segment: bytes):
        self.seq_num = Struct.unpack("I", segment[0:4])[0]
        self.ack_num = Struct.unpack("I", segment[4:8])[0]
        self.flag = SegmentFlag(Struct.unpack("B", segment[8:9])[0])
        self.checksum = Struct.unpack("H", segment[10:12])[0]
        self.payload = segment[12:]