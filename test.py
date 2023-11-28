from lib.FileParser import *
from lib.Segment import *


file = FileParser("test\hello.txt", True)
num_seg = file.get_count_segment()

segments: list[Segment] = []
for i in range(num_seg):
    segment = Segment()
    segment.set_payload(file.get_chunk(i))
    print(segment)
    segments.append(segment)

file_write = FileParser("out")

for i in range(num_seg):
    file_write.write_to_buffer(segments[i].get_payload())

file_write.write_to_buffer(b" add some")