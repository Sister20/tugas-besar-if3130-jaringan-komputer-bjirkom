import os
from math import *
from io import *
from .constant import *

class FileParser:

    def __init__(self, path: str, is_server: bool = False):
        self.path: str = path
        if is_server:
            self.file_binary_buffer: BufferedReader = self.parse_file()
        else:
            if not os.path.exists(self.path):
                os.makedirs(path)
            
    def parse_file(self) -> BufferedReader:
        try:
            file = open(f"{self.path}", "rb")
            return file
        except FileNotFoundError as err:
            print(f"[!] {err} ")
            print(f"[!] {self.path} does not exists...")
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

    def get_chunk(self, page: int):
        offset = MAX_PAYLOAD * page
        self.file_binary_buffer.seek(offset)
        return self.file_binary_buffer.read(MAX_PAYLOAD)
    
    def get_count_segment(self) -> int:
        return ceil(self.get_size()/MAX_PAYLOAD)
    
    def generate_file(self) -> BufferedWriter:
        try:
            file = open(self.path, "wb")
            return file
            
        except FileNotFoundError as err:
            print(f"[!] {err} ")
            print(f"[!] {self.path} does not exists...")
            exit(1)
    
    def write_to_buffer(self, payload: bytes):
        self.file_binary_buffer.write(payload)

    def parse_metadata(self, payload: bytes):
        metadata = payload.decode().split(",")
        self.path += '/' + metadata[0] + "." + metadata[1]
        self.file_binary_buffer: BufferedWriter = self.generate_file()
        return { "name" : metadata[0], "ext": metadata[1], "size": metadata[2] }

if __name__ == "__main__":
    file = FileParser("test\hello.txt")
    print(file.path)
