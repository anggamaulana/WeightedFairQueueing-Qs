import socket
import sys
import time

HOST = '0.0.0.0'
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
daddr=('35.229.112.213',8083)
# daddr = ('localhost',8083)
fifo = []
while True:
	d = s.recvfrom(1024)
	data = d[0]
	addr = d[1]
	if data == "dest":
		daddr = addr
		s.sendto("connected", daddr)
	else:
		fifo.append(data)
	print 'length', len(fifo)
	if daddr and len(fifo) != 0:
		# s.sendto(fifo[0], daddr)
		print 'sending to dest', fifo[0]
		try:
			# s.sendto(data, daddr)		
			s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s2.connect(daddr)
			print("connect to ", daddr)
			data += ';'
			s2.send(data)
			s2.close()
		except Exception as e:
			print(e)
		fifo.pop(0)
		print 'popping'
	if not data:
		break
	time.sleep(0.5)
s.close()