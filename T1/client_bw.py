#!/usr/bin/python3
# Echo client program
# Version con dos threads: uno lee de stdin hacia el socket y el otro al revés
import jsockets
import sys, threading
import time

def Rdr(s):
    while True:
        try:
            data=s.recv(1500)
        except:
            data = None
        if not data: 
            break
        sys.stdout.buffer.write(data)
        sys.stdout.flush()

if len(sys.argv) != 4:
    print('Use: '+sys.argv[0]+' size host port < input > output')
    sys.exit(1)

''' orden de los argssss:     
0 -> client_echo3.py 
1 -> size
2 -> host
3 -> port
4? -> in
5? -> out
'''
s = jsockets.socket_tcp_connect(sys.argv[2], sys.argv[3])
if s is None:
    print('could not open socket')
    sys.exit(1)

# Creo thread que lee desde el socket hacia stdout:
newthread = threading.Thread(target=Rdr, args=(s,))
newthread.start()

# En este otro thread leo desde stdin.buffer hacia socket, considerando el size recibido:
while True:
    chunk = (sys.stdin.buffer.read(int(sys.argv[1])))
    if not chunk:
        break
    s.send(chunk)

s.close()

