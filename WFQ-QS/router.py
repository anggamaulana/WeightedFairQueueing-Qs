import socket
import sys
import time
import threading

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
daddr=None
globalTime = None
flag = 0
rDash = 0
l_avg_prev = 0
lambda_bandwidth=1

def recvpacket():
	global source
	global flag
	global rDash
	while True:
		d = s.recvfrom(1024)
		recvTime = current_milli_time()
		sourcey, data = d[0].split(';')
		sourcey = int(sourcey)
		print data
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
		if len(source[sourcey]['fno']) == 0:
			print 'First packet'
			fno = roundNumber + (packet_size[sourcey]*1.0/numpackets[sourcey])
			source[sourcey]['fno'].append(fno)
		else:
			print 'length', len(source[sourcey]['fno']), 'source', sourcey

			
			PacketLength = packet_size[sourcey]
			TDelay = 0.1
			f1=0.01
			queue_len = len(source[sourcey]['fno'])

			global l_avg_prev

			l_avg = (1-f1) * l_avg_prev + f1 * queue_len
			print("l_avg = (1-%f) * %f + %f * %d: " % (f1,l_avg_prev,f1,queue_len))
			print("nilai l_avg : ", l_avg)
			print("weight : ", numpackets)

			l_avg_prev = queue_len


			if sourcey==0:
				# antrian prioritas tinggi w1
				minth1=0.833
				maxth1=3.667
				upper=0.7
				wp=0.3
				if l_avg<minth1:
					numpackets[sourcey] = wp
				elif l_avg>minth1 and l_avg<maxth1:
					numpackets[sourcey] = (upper-wp)*(l_avg-minth1)*(1.0/(maxth1-minth1))
				elif l_avg>=maxth1:
					numpackets[sourcey] = upper

			elif sourcey==1:
				# antrian prioritas  w1
				med_init=0.3
				minth2 = 0.83

				if l_avg < minth2:
					numpackets[sourcey] = med_init
				elif l_avg >= minth2:
					numpackets[sourcey] = 1-numpackets[0]

			elif sourcey==2:
				# antrian prioritas w3
				numpackets[sourcey] = 1-(numpackets[0]+numpackets[1])

			tVirtualPrev = source[sourcey]['fno'][ queue_len - 1]
			weightF = numpackets[sourcey]*lambda_bandwidth

			
			fno = max(roundNumber+TDelay, tVirtualPrev) + (PacketLength * 1.0 / weightF)

			if sourcey==2:
				fno = min(roundNumber+TDelay, tVirtualPrev) + (PacketLength * 1.0 / weightF)


			# masukkan paket prioritas 'sourcey' ke antrian
			# jika antrian penuh maka masuk ke waiting list dengan durasi menunggu
			# jika paket melebihi durasi menunggu maka akan didrop 
			waiting_list_duration = 0.3

			source[sourcey]['fno'].append(fno)

		source[sourcey]['time'].append(recvTime - globalTime)
		source[sourcey]['data'].append(str(sourcey) + ';' + data)
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
		if daddr:
			mini = 999999999999999
			index = 0
			so = 0
			for i in xrange(3):
				for j in xrange(len(source[i]['fno'])):
					if source[i]['sent'][j] == 0:
						if source[i]['fno'][j] < mini:
							mini = min(source[i]['fno'])
							index = j
							so = i
			if mini != 999999999999999:
				s.sendto(source[so]['data'][index], daddr)
			source[so]['sent'][index] = 1
			time.sleep(sleeptime[so])

t1 = threading.Thread(target=recvpacket)
t1.daemon = True
t2 = threading.Thread(target=sendpacket)
t2.daemon = True

t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)