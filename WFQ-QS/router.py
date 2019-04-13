import socket
import sys
import time
import threading
import pytz, datetime

HOST = '127.0.0.1'
PORT = 8888



current_milli_time = lambda: int(round(time.time() * 1000))

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
roundNumber = 0
activeConn = 0
source = {0:{'time':[],'data':[], 'fno':[], 'active':0, 'sent':[0]}, 1:{'time':[], 'data':[], 'fno':[], 'active':0, 'sent':[0]}, 2:{'time':[], 'data':[], 'fno':[], 'active':0, 'sent':[0]}}
packet_size = [100, 50, 100]
iters = {0:0, 1:0, 2:0}
count = 0
# numpackets=[10, 15, 20]
numpackets=[0.3, 0.3, 0.4]
sleeptime=[0.1,0.05,0.1]
daddr=('35.229.112.213',8083)
daddr = ('localhost',8083)
# daddr = None
globalTime = None
flag = 0
rDash = 0
l_avg_prev = 0
lambda_bandwidth=1

tVirtual = [0,0,0]
MAX_BUFFER = [100,100,100]


def recvpacket():
	global source
	global flag
	global rDash
	while True:
		d = s.recvfrom(1024)
		recvTime = current_milli_time()
		sourcey, data = d[0].split(';')
		tm = datetime.datetime.now().replace(tzinfo=pytz.utc).isoformat()
		sourcey = int(sourcey)
		
		if data == "dest":
			global daddr
			daddr= d[1]
			s.sendto("connected", daddr)
			continue
		if flag == 0:
			prevTime = 0
			globalTime = recvTime
			roundNumber = 0
			flag = 1

		# DROP PACKET IF BUFFER FULL
		if len(source[sourcey]['fno']) == MAX_BUFFER[sourcey]:
			print("DROP PACKET")
			continue

		if len(source[sourcey]['fno']) == 0:
			print 'First packet'
			fno = roundNumber + (packet_size[sourcey]*1.0/numpackets[sourcey])
			source[sourcey]['fno'].append(fno)
		else:
			print 'length', len(source[sourcey]['fno']), 'source', sourcey

		source[sourcey]['time'].append(recvTime - globalTime)
		source[sourcey]['data'].append(str(sourcey) + ';' + data+';'+tm)
		source[sourcey]['sent'].append(0)
		roundNumber += ((recvTime - globalTime) - prevTime)*rDash
		lFno = max(source[sourcey]['fno'])
		print lFno, roundNumber
		if lFno > roundNumber:
			source[sourcey]['active'] = 1
		else:
			source[sourcey]['active'] = 0
		weightsSum = 0
		for i in xrange(3):
			if source[i]['active'] == 1:
				weightsSum += numpackets[i]
		if weightsSum == 0:
			continue
		rDash = 1.0/weightsSum
		prevTime = recvTime - globalTime
	s.close()

def sendpacket():
	while True:

		# PEMBOBOTAN
		
		for sourcey in range(3):
			PacketLength = packet_size[sourcey]
			if sourcey == 0:
				TDelay = 0.001
			elif sourcey == 1:
				TDelay = 0.01
			elif sourcey == 2:
				TDelay = 0.1

			f1=0.01
			queue_len = len(source[sourcey]['fno'])
			if queue_len==0:
				continue
			else:
				source[sourcey]['fno'].pop(0)

			global l_avg_prev

			l_avg = (1-f1) * l_avg_prev + f1 * queue_len
			print("l_avg = (1-%f) * %f + %f * %d: " % (f1,l_avg_prev,f1,queue_len))
			print("nilai l_avg : ", l_avg)
			print("weight : ", numpackets)

			l_avg_prev = l_avg
				

			if sourcey==0:
				# antrian prioritas tinggi w1
				minth1=25
				maxth1=50
				upper=0.7
				wp=0.3
				if l_avg<minth1:
					numpackets[sourcey] = wp
					print("p0 th1")
				elif l_avg>minth1 and l_avg<maxth1:
					numpackets[sourcey] = ((upper-wp)*(l_avg-minth1)*(1.0/(maxth1-minth1)))+wp
					# numpackets[sourcey] = ((0.3/(maxth1-minth1))*(abs(l_avg-l_avg_prev))+numpackets[sourcey])
					print("p0 th2")
				elif l_avg>=maxth1:
					numpackets[sourcey] = upper
					print("p0 th3")

			elif sourcey==1:
				# antrian prioritas  w1
				med_init=0.3
				minth2 = 50
				if l_avg < minth2:
					numpackets[sourcey] = med_init
					print("p1 th1")
				elif l_avg >= minth2:
					numpackets[sourcey] = 1-numpackets[0]
					print("p1 th2")
				

			elif sourcey==2:
				# antrian prioritas w3
				numpackets[sourcey] = 1-(numpackets[0]+numpackets[1])
				print("p2 th1")

			
			if numpackets[sourcey]==0:
				numpackets[sourcey]=0.0001
				

			# print("weigh now",numpackets)
			weightF = numpackets[sourcey]*lambda_bandwidth

			global tVirtual

			

			

			arrive = source[sourcey]['time'].pop(0)
			fno = min(arrive+TDelay, tVirtual[sourcey]) + (PacketLength * 1.0 / weightF)

			if sourcey==2:
				fno = max(arrive+TDelay, tVirtual[sourcey]) + (PacketLength * 1.0 / weightF)

			

			tVirtual[sourcey] = fno
			# source[sourcey]['fno'].append(fno)


		if daddr:

			minv = 1000000000
			min_priority=0
			for i in range(len(tVirtual)):
				if tVirtual[i]<minv and tVirtual[i]!=0 and len(source[i]['data'])>0:
					minv = tVirtual[i]
					min_priority = i

			
			if len(source[min_priority]['data'])>0:
				data = source[min_priority]['data'].pop(0)
				
				try:
					# s.sendto(data, daddr)		
					s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s2.connect(daddr)
					print("connect to ", daddr)
					data += ';'+';'.join([str(i) for i in numpackets])
					print("data prioritas ",min_priority," dikirim dengan data ", data)
					s2.send(data)
					s2.close()
				except Exception as e:
					print(e)
			
			

			
			time.sleep(sleeptime[min_priority])

t1 = threading.Thread(target=recvpacket)
t1.daemon = True
t2 = threading.Thread(target=sendpacket)
t2.daemon = True

t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)