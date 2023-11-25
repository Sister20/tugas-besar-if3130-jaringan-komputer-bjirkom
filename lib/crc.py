POLYNOM = 0x1021  # x^16 + x^12 + x^5 + 1 (CRC-16/CCITT)


class CRC:
    """
    CRC-16/CCITT
    Most significant bit first (big endian)
    """

    def __init__(self, data: bytes):
        self.data = data
        self.length = len(data)

    def calculate_reminder(self):
        reminder = 0
        for i in range(self.length):
            reminder = reminder ^ (self.data[i] << 8)
            for j in range(8):
                if reminder & 0x8000:
                    reminder = (reminder << 1) ^ POLYNOM
                else:
                    reminder <<= 1
                reminder &= 0xFFFF

        return reminder
