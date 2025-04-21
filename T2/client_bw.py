#!/usr/bin/python3
# Echo client program
import jsockets
import sys, threading
from threading import Lock
import socket as socket 

mutex_lock = Lock()

done_event = threading.Event()
bytes_sent = 0
bytes_recieved = 0

def Rdr(s):
    global bytes_recieved
    s.settimeout(3)
    with open(outp, 'wb') as outfile:
        while True:
            try:
                data = s.recv(size)
                if not data or data == b'': 
                    print("EOF marcador")
                    break
                bytes_recieved += len(data)
                outfile.write(data)
            except socket.timeout:
                print("Timeout alcanzado")
                break
    with mutex_lock:
        done_event.set()


if len(sys.argv) != 6:
    print('Use: '+sys.argv[0]+' size input output host port')
    sys.exit(1)

size = int(sys.argv[1])
inp = sys.argv[2]
outp = sys.argv[3]
host = sys.argv[4]
port = sys.argv[5]

s = jsockets.socket_udp_connect(host, port)
if s is None:
    print('could not open socket')
    sys.exit(1)

newthread = threading.Thread(target=Rdr, args=(s,))
newthread.start()

with open(inp, 'rb') as infile:
    while True:
        chunk = infile.read(size)
        if not chunk:
            break
        bytes_sent += s.send(chunk)
s.send(b'')

newthread.join()

print("Bytes enviados: ", bytes_sent)
print("Bytes recibidos: ", bytes_recieved)

s.close()