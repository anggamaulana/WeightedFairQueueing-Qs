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
                st.append(st[2])
                delay = kirim-dtng
                st[2] = str(delay.total_seconds())
                st[6] = float(st[6])
                st[7] = float(st[7])
                
                rows.append(st)
            except Exception as e:
                rows.append(data)
                continue

        conn.close()
except KeyboardInterrupt as k:
    print("sedang menyimpan report")
    # print(rows)
    try:
        data = pd.DataFrame(data=rows, columns=['prioritas','data','delay','bobot1','bobot2','bobot3','tArrive','tFinish','formula p1','formula p2','formula p3','waktu datang'])

        arrival_time = data['tArrive'].apply(lambda x: x-data['tArrive'][0])
        finish_time = data['tFinish'].apply(lambda x: x-data['tArrive'][0])

        data['tFinish'] = finish_time
        data['tArrive'] = arrival_time

        # print(data.head())
        data.to_excel("report.xlsx")
        s.close()
    except Exception as e:
        print(e)
    print("done")
