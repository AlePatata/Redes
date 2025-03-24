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

if len(sys.argv) != 3:
    print('Use: '+sys.argv[0]+' host port')
    sys.exit(1)

s = jsockets.socket_udp_connect(sys.argv[1], sys.argv[2])
if s is None:
    print('could not open socket')
    sys.exit(1)

# Esto es para dejar tiempo al server para conectar el socket
s.send(b'hola')
s.recv(1024)

# Creo thread que lee desde el socket hacia stdout:
newthread = threading.Thread(target=Rdr, args=(s,))
newthread.start()

# En este otro thread leo desde stdin hacia socket:
try:
    while True:
        chunk = ( sys.stdin.buffer.read(1024))
        if not chunk:
            break
        s.send(chunk)
except:
    pass

time.sleep(3)  # dar tiempo para que vuelva la respuesta
s.close()

