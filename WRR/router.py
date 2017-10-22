import socket
import sys
import time

HOST = '127.0.0.1'
PORT = 8888

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	print 'Socket created'
except socket.error, msg:
	print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()
	 
print 'Socket bind complete'
daddr = None
source = {0:[], 1:[], 2:[]}
packet_size = [100, 50, 100]
iters = {0:0, 1:0, 2:0}
count = 0

while True:
	d = s.recvfrom(1024)
	sourcey, data = d[0].split(';')
	addr = d[1]
	print data
	if data == "dest":
		daddr = addr
		s.sendto("connected", daddr)
	else:
		source[int(sourcey)].append(sourcey + ';' + data)
	position = count%3
	if daddr and len(source[position]) != 0:
		if iters[position] >= packet_size[position]:
			s.sendto(source[position][i], daddr)
			print 'sending to dest', source[position][i]
			source[position].pop(0)
			print 'popping'
			iters[position] = 0
	count += 1
	for i in xrange(3):
		iters[i] += 1
	if not data:
		break
	time.sleep(0.5)
s.close()