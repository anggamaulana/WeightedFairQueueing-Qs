import socket
import dateutil.parser
import datetime
import pytz
import pandas as pd
from datetime import timedelta


TCP_IP = '0.0.0.0'
TCP_PORT = 8083
BUFFER_SIZE = 1024  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # buka soceket penerima data
s.bind((TCP_IP, TCP_PORT)) # ikat ke port tertentu
s.listen(1) # merekan data yg masuk
rows = []

# local 1 minutes ahead
serverlocaldiff=timedelta(seconds=1) #penyesuaian karena dicloud dan lokal selisih satu detik

print ('Connection address:')
try:
    while 1:
        conn, addr = s.accept() # terima data dari router
        data = conn.recv(BUFFER_SIZE) # terima data dari router
        if data:
            print ("received data:", data)
            try:
                st = data.split(';') # belah data berdasakan karakter ';' dan jadikan array

                dtng = dateutil.parser.parse(st[2])-serverlocaldiff # ubah string menjadi waktu bawaan python
                # dtng = dateutil.parser.parse(st[2])
                kirim = datetime.datetime.utcnow() # ubah waktu ke bentuk utc
                st.append(st[2])
                delay = kirim-dtng
                st[2] = str(delay.total_seconds())
                st[6] = float(st[6])
                st[7] = float(st[7])
                
                rows.append(st) #masukkan ke array row untuk laporan ke excel
            except Exception as e:
                rows.append(data)
                continue

        conn.close() # tutup koneksi dengan paket data saat ini
except KeyboardInterrupt as k:
    print("sedang menyimpan report")
    # print(rows)
    try:
        data = pd.DataFrame(data=rows, columns=['prioritas','data','delay','bobot1','bobot2','bobot3','tArrive','tFinish','tarrive (waktu tiba di router)','treceive (waktu sampai di cloud)','bobot / bobot minimal','jumlah isi buffer','l_avg','formula p1','formula p2','formula p3','antrian','l_avg_0','l_avg_1','l_avg_2',
        'vt_0','vt_1','vt_2','waktu datang'])

        arrival_time = data['tArrive'].apply(lambda x: x-data['tArrive'][0])
        finish_time = data['tFinish'].apply(lambda x: x-data['tArrive'][0])

        data['tFinish'] = finish_time
        data['tArrive'] = arrival_time

        print(data.head())
        data.to_excel("report.xlsx")
        s.close()
    except Exception as e:
        print(e)
    print("done")
