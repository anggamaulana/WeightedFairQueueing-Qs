import socket
import sys
import threading

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

host = 'localhost'
port = 8888


HOST = 'localhost'
PORT = 8088

try:
    s.bind((HOST, PORT))
    print("bind ", HOST, PORT)
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

# s.sendto("-1;dest", (host, port))


while True:
    print("receivingczzz")
    try:

        d = s.recvfrom(1024)
        print("receiving", d)
        reply = d[0]
        addr = d[1]
        print 'Server reply : ' + reply
    except Exception as e:
        # print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        print(e)
        sys.exit()
    print("end")
