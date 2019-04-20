import socket
import dateutil.parser
import datetime
import pytz
import pandas as pd
from datetime import timedelta


TCP_IP = '0.0.0.0'
TCP_PORT = 8083
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
rows = []

# local 1 minutes ahead
serverlocaldiff=timedelta(minutes=1)

print ('Connection address:')
try:
    while 1:
        conn, addr = s.accept()
        data = conn.recv(BUFFER_SIZE)
        if data:
            print ("received data:", data)
            try:
                st = data.split(';')

                # dtng = dateutil.parser.parse(st[2])-serverlocaldiff
                dtng = dateutil.parser.parse(st[2])
                kirim = datetime.datetime.utcnow()

                delay = kirim-dtng
                st[2] = str(delay.total_seconds())
                rows.append(st)
            except Exception as e:
                rows.append(data)
                continue

        conn.close()
except KeyboardInterrupt as k:
    print("sedang menyimpan")
    data = pd.DataFrame(data=rows, columns=['prioritas','data','delay','bobot1','bobot2','bobot3'])
    data.to_excel("report.xlsx")
    s.close()
    print("done")
