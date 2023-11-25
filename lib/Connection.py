import socket
import sys
from constant import MAX_SEGMENT

class Connection:
  def __init__(self, ip : str,  port : int):
    self.ip = ip
    self.port = port

    # set the socker to datagram
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # set options to reuse address and port
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if (sys.platform != 'win32'):
      self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    self.socket.bind((self.ip, self.port))
    print(f"[!] Server started at {self.ip}:{self.port}")

  def listenMsg(self):
    while (True):
      bytesAddressPair = self.socket.recvfrom(MAX_SEGMENT)
      
      msg = bytesAddressPair[0]
      address = bytesAddressPair[1]

      return msg, address

  def sendMsg(self, msg, dest):
    self.socket.sendto(msg, dest)

  def closeSocket(self):
    self.socket.close()