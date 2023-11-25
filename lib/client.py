from Connection import *

ip_client           = "127.0.0.2"
port_client         = 3002

ip_server           = "127.0.0.1"
port_server         = 3001

msgFromServer       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromServer)

client = Connection("127.0.0.2", 3002)
client.sendMsg(bytesToSend, (ip_server, port_server))

msg, address = client.listenMsg()

print(f"Server's message : {msg}")
print(f"Server's IP      : {address}" )
client.closeSocket()