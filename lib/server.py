from Connection import *

ip_server           = "127.0.0.1"
port_server         = 3001

msgFromServer       = "Hello UDP Client"
bytesToSend         = str.encode(msgFromServer)

server = Connection(ip_server, port_server)
msg, address = server.listenMsg()

print(f"Client's message : {msg}")
print(f"Client's IP      : {address}" )

server.sendMsg(bytesToSend, address)
server.closeSocket()