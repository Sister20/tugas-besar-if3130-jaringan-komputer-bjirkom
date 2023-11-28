from lib.FileParser import *
from lib.Segment import *


file = FileParser("test\\2023-09-27 16-09-05.mkv", True)
num_seg = file.get_count_segment()
print(file.get_size())

segments: list[Segment] = []
for i in range(num_seg):
    segment = Segment()
    segment.set_payload(file.get_chunk(i))

    print(f"size - {i} - {len(file.get_chunk(i))}")
    
    # print(str(segment) + "\n")
    segments.append(segment)

file_write = FileParser("out\\video.mkv")

for i in range(num_seg):
    file_write.write_to_buffer(segments[i].get_payload())

file_write.write_to_buffer(b" add some")