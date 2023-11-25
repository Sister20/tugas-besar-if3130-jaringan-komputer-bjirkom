from .constant import *
import struct


class SegmentFlag:

    """
    @attribute syn: boolean
    @attribute ack: boolean
    @attribute fin: boolean
    """

    def __init__(self, flag: bytes):
        self.syn: bytes = SYN_FLAG & flag
        self.ack: bytes = ACK_FLAG & flag
        self.fin: bytes = FIN_FLAG & flag

    def get_flag_bytes(self) -> bytes:
        return struct.pack("B", self.ack | self.syn | self.fin)
