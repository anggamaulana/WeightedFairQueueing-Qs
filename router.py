import socket
import sys
import time

HOST = '127.0.0.1'   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
# Datagram (udp) socket
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print 'Socket created'
except socket.error, msg:
	print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
 
 
# Bind socket to local host and port
try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
	 
print 'Socket bind complete'
daddr = None
fifo = []
while True:
	d = s.recvfrom(1024)
	data = d[0]
	addr = d[1]
	if data == "dest":
		daddr = addr
		s.sendto("connected", daddr)
		# print 'Message[' + daddr[0] + ':' + str(daddr[1]) + '] - ' + data.strip()
	else:
		fifo.append(data)
	if daddr and len(fifo) != 0:
			s.sendto(fifo[0], daddr)
			fifo.pop(0)
	# else:
	# 	s.sendto(reply, addr) 
	if not data:
		break
	time.sleep(0.5)
	 
s.close()