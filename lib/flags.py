from .Segment import Segment


class Flags:
    @staticmethod
    def syn(seq_num: int) -> Segment:
        syn_segment = Segment()
        syn_segment.set_flag(["SYN"])
        syn_segment.set_seq(seq_num)
        return syn_segment

    @staticmethod
    def ack(seq_num: int, ack_num: int) -> Segment:
        ack_segment = Segment()
        ack_segment.set_flag(["ACK"])
        ack_segment.set_seq(seq_num)
        ack_segment.set_ack(ack_num)
        return ack_segment

    @staticmethod
    def syn_ack(seq_num: int, ack_num: int) -> Segment:
        syn_ack_segment = Segment()
        syn_ack_segment.set_flag(["SYN", "ACK"])
        syn_ack_segment.set_seq(seq_num)
        syn_ack_segment.set_ack(ack_num)
        return syn_ack_segment

    # TODO: implement fin and fin_ack
    @staticmethod
    def fin(seq_num: int) -> Segment:
        fin_segment = Segment()
        fin_segment.set_flag(["FIN"])
        fin_segment.set_seq(seq_num)
        return fin_segment

    @staticmethod
    def fin_ack(seq_num: int, ack_num: int) -> Segment:
        fin_ack_segment = Segment()
        fin_ack_segment.set_flag(["FIN", "ACK"])
        fin_ack_segment.set_seq(seq_num)
        fin_ack_segment.set_ack(ack_num)
        return fin_ack_segment
