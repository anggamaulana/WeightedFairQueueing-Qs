import socket
import sys
import time
import datetime

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()

host = 'localhost'
port = 8888
packet_count = [300, 300, 300]
packet_interval = [1, 1, 1]
packet_size = [100, 50, 100]
i = int(sys.argv[1])
for j in xrange(packet_count[i]):
    try:
        msg = str(i) + ';vishalisalltimethope' + str(j + 1)
        s.sendto(msg, (host, port))
    except socket.error, msg:
        print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
    time.sleep(packet_interval[i])
