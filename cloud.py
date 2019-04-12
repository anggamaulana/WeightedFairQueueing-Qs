import socket
import dateutil.parser
import datetime
import pytz


TCP_IP = '0.0.0.0'
TCP_PORT = 8083
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
rows = []

print ('Connection address:')
try:
    while 1:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE)
        if data:
            print ("received data:", data)
            st = data.split(';')

            dtng = dateutil.parser.parse(st[2])
            kirim = datetime.datetime.now().replace(tzinfo=pytz.utc)

            delay = kirim-dtng
            st[2] = str(delay.total_seconds())
            rows.append(st)

        conn.close()
except KeyboardInterrupt as k:
    print(rows)
    s.close()
