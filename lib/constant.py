SYN_FLAG = 0b000000010  # 2
ACK_FLAG = 0b000010000  # 16
FIN_FLAG = 0b000000001  # 1
MAX_SEGMENT = 32768
MAX_PAYLOAD = 32756
POLYNOM = 0x1021  # x^16 + x^12 + x^5 + 1 (CRC-16/CCITT)
TIMEOUT = 3 # seconds
LISTEN_TIMEOUT = 60 # seconds
QUEUE_TIMEOUT = 30 # 5 minute
WINDOW_SIZE = 3