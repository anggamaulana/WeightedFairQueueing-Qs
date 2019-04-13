import socket
import sys
import time
import threading
import pytz
import datetime
from fractions import gcd


HOST = '127.0.0.1'
PORT = 8888


def current_milli_time(): return int(round(time.time() * 1000))

MAX_BUFFER = [100, 100, 100]
def reduce_ratio(numbers):
    minn = 1000000000000
    for i in range(len(numbers)):
		if minn>numbers[i] and numbers[i]!=0:
			minn = numbers[i]
    solved = [min(int(i/minn),max(MAX_BUFFER))  for i in numbers]
    return solved


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg:
    print 'Failed to create socket. Error Code : ' + \
        str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

print 'Socket bind complete'
daddr = None
source = {0: [], 1: [], 2: []}
packet_size = [100, 50, 100]
iters = {0: 0, 1: 0, 2: 0}
count = 0
numpackets = [2, 8, 1]
sleeptime = [0.1, 0.05, 0.1]
daddr = ('35.229.112.213', 8083)
daddr = ('localhost', 8083)

l_avg_prev = 0
lambda_bandwidth = 1

tVirtual = [0, 0, 0]



def recvpacket():
    global source
    global daddr
    while True:
        d = s.recvfrom(1024)
        sourcey, data = d[0].split(';')
        tm = datetime.datetime.now().replace(tzinfo=pytz.utc).isoformat()
        recvTime = current_milli_time()

        # print datap
        sourcey = int(sourcey)

        if len(source[sourcey]) == 0:
            globalTime = recvTime
            
        else:
            # DROP PACKET IF BUFFER FULL
            if len(source[sourcey]) == MAX_BUFFER[sourcey]:
				print("DROP PACKET")
				continue

        if data == "dest":
            
            daddr = d[1]
            s.sendto("connected", daddr)
        else:
            # print(recvTime - globalTime)
            tme = str(recvTime - globalTime)
            source[int(sourcey)].append(str(sourcey) + ';' + data + ';' + tm)
            # print(source)
    s.close()


def sendpacket():
	num = [0, 0, 0]
	global numpackets
	print("sending packet")

	while True:

        # PEMBOBOTAN

		for sourcey in range(3):
			PacketLength = packet_size[sourcey]
			TDelay = 0.1
			f1 = 0.01
			queue_len = len(source[sourcey])
			if queue_len == 0:
				continue
			

			global l_avg_prev

			l_avg = (1-f1) * l_avg_prev + f1 * queue_len
			# print("l_avg = (1-%f) * %f + %f * %d: " %
			# 		(f1, l_avg_prev, f1, queue_len))
			# print("nilai l_avg : ", l_avg)
			# print("weight : ", numpackets)

			l_avg_prev = queue_len

			if sourcey == 0:
				# antrian prioritas tinggi w1
				minth1 = 0.833
				maxth1 = 3.667
				upper = 0.6
				wp = 0.3
				if l_avg < minth1:
					numpackets[sourcey] = wp
					# print("p0 th1")
				elif l_avg > minth1 and l_avg < maxth1:
					# numpackets[sourcey] = (upper-wp)*(l_avg-minth1)*(1.0/(maxth1-minth1))
					numpackets[sourcey] = (
						(0.3/(maxth1-minth1))*(abs(l_avg-l_avg_prev))+numpackets[sourcey])
					# print("p0 th2")
				elif l_avg >= maxth1:
					numpackets[sourcey] = upper
					# print("p0 th3")

			elif sourcey == 1:
				# antrian prioritas  w1
				med_init = 0.3
				minth2 = 0.83
				if l_avg < minth2:
					numpackets[sourcey] = med_init
					print("p1 th1")
				elif l_avg >= minth2:
					numpackets[sourcey] = 1-numpackets[0]
					print("p1 th2")

			elif sourcey == 2:
				# antrian prioritas w3
				numpackets[sourcey] = 1-(numpackets[0]+numpackets[1])
				print("p2 th1")

			if numpackets[sourcey] == 0:
				numpackets[sourcey] = 0.0001

			# print("weigh now",numpackets)
			weightF = numpackets[sourcey]*lambda_bandwidth

			# PEMBOBOTAN END

		
		if daddr:

			# Pembulatan bobot
			numpackets = reduce_ratio(numpackets)
			# print("numpacket now",numpackets, "reduce", numpackets_reduce)
			
			for j in range(3):
				
				for i in range(int(numpackets[j])):
					
					if len(source[j]) == 0:
						continue
					else:
						# s.sendto(source[j][0], daddr)
						try:
							# s.sendto(data, daddr)
							s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							s2.connect(daddr)
							print("numpacket now",numpackets)
							print("connect to ", daddr, "and send ", source[j][0])
							s2.send(source[j].pop(0))
							s2.close()
						except Exception as e:
							print(e)

						num[j] += 1
						# del source[j][0]
						time.sleep(sleeptime[j])
#			print num
		


t1 = threading.Thread(target=recvpacket)
t2 = threading.Thread(target=sendpacket)
t1.daemon = True
t2.daemon = True
t1.start()
t2.start()

while threading.active_count() > 0:
    time.sleep(0.1)
