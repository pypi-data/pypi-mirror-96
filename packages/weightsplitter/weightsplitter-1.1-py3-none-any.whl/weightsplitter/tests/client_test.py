from socket import socket


sock = socket()
sock.connect(('192.168.100.109', 2290))
while True:
    data = sock.recv(1024)
    print(data)