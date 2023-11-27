import os
from math import *
from io import *
from .constant import *

class FileParser:

    def __init__(self, path: str):
        self.path: str = path
        self.file_binary_buffer: BufferedReader = self.parse_file()

    
    def parse_file(self) -> BufferedReader:
        try:
            file = open(f"{self.path}", "rb")
            return file
        except:
            print(f"[!] {self.path} doesn't exists. Exiting...")
            exit(1)
    
    def get_filename(self) -> str :
        if ( "\\" in self.path ):
            return self.path.split("\\")[-1]
        elif ( "/" in self.path ):
            return self.path.split("/")[-1]
        
        return self.path
    
    def get_extension(self) -> str :
        return self.get_filename().split(".")[-1]
    
    def get_name(self) -> str :
        return self.get_filename().split(".")[0]
    
    def get_size(self) -> int :
        return os.path.getsize(self.path)

    def get_chunck(self, page: int):
        offset = MAX_PAYLOAD * page
        self.file_binary_buffer.seek(offset)
        return self.file_binary_buffer.read(MAX_PAYLOAD)
    
    def get_count_segment(self) -> int:
        return ceil(self.get_size()/MAX_PAYLOAD)

if __name__ == "__main__":
    file = FileParser("test\hello.txt")
    print(file.path)
