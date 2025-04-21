#!/usr/bin/python3
# Echo client program
import jsockets
import sys, threading

done_event = threading.Event()

def Rdr(s, size, out):
    with open(out, 'wb') as outfile:
        while not done_event.is_set():
            try:
                data=s.recv(size)
            except:
                data = None
            if not data: 
                break                
            outfile.write(data)


''' orden de los argssss:     
0 -> client_echo3.py 
1 -> size
2 -> in
3 -> out
4 -> host
5 -> port
'''

if len(sys.argv) != 6:
    print('Use: '+sys.argv[0]+' size input output host port')
    sys.exit(1)

s = jsockets.socket_tcp_connect(sys.argv[4], sys.argv[5])
if s is None:
    print('could not open socket')
    sys.exit(1)

size = int(sys.argv[1]) 

newthread = threading.Thread(target=Rdr, args=(s, size, sys.argv[3]))
newthread.start()

with open(sys.argv[2], 'rb') as infile:
    while True:
        chunk = infile.read(size)
        if not chunk:
            break
        s.sendall(chunk)

done_event.set()
newthread.join()

s.close()