#!/usr/bin/python3
# Echo client program
import jsockets
import sys, threading
from threading import Lock, Condition
import socket as socket 

mutex_lock = Lock()
condition = Condition()

done_event = threading.Event()
bytes_sent = 0       # Without resending packages
bytes_sent_total = 0 # Counting the re-sent packages
bytes_received = 0
errors = 0
akn_to_sender = -1

def format(i):
    return str(i).zfill(3).encode()

def Rdr(s):
    global bytes_received
    global akn_to_sender
    s.settimeout(3)
    with open(outp, 'wb') as outfile:
        while True:
            try:
                total_data = s.recv(size + 3)
                bytes_received += len(total_data)
                akn_received = total_data[:3].decode(errors='ignore')
                data = total_data[3:]
                with condition:
                    print("AKN received: ", akn_received)
                    akn_to_sender = int(akn_received)
                    if not data or data == b'':
                        print("EOF marcador")
                        break
                    condition.notify()
                outfile.write(data)
            except socket.timeout:
                print("Timeout alcanzado en receptor")
                break
    with mutex_lock:
        done_event.set()


if len(sys.argv) != 7:
    print('Use: '+sys.argv[0]+' size timeout input output host port')
    sys.exit(1)

size = int(sys.argv[1])
timeout = float(sys.argv[2])
inp = sys.argv[3]
outp = sys.argv[4]
host = sys.argv[5]
port = sys.argv[6]

s = jsockets.socket_udp_connect(host, port)
if s is None:
    print('could not open socket')
    sys.exit(1)

newthread = threading.Thread(target=Rdr, args=(s,))
newthread.start()

with open(inp, 'rb') as infile:
    akn_to_writer = 0
    while True:
        chunk = infile.read(size)
        byte_array_akn = format(akn_to_writer)  

        if not chunk:
            chunk = b''
            print(f'Sending EOF message with AKN: {(byte_array_akn+chunk).decode()}')
        else:
            print(f'Trying to send package with AKN: {byte_array_akn.decode()}')

        increment = s.send(byte_array_akn+chunk)
        bytes_sent += increment
        bytes_sent_total += increment
        
        with condition:
            # Si la variable global no actualizó al mismo akn que le mandé me quedo esperando
            while akn_to_sender != akn_to_writer: 
                condition.wait(timeout=timeout)
                if akn_to_sender != akn_to_writer:
                    print(f'Timeout alcanzado en emisor: AKN {byte_array_akn.decode()} no recibido')
                    errors += 1                                      # Aumentamos errores
                    akn_to_writer = (akn_to_writer + 1)%1000
                    byte_array_akn = format(akn_to_writer)
                    print(f'Re-Sending package with AKN: {byte_array_akn.decode()}')
                    bytes_sent_total += s.send(byte_array_akn+chunk) # Enviamos de nuevo

            # Si se cumplió que la variable global es la misma que mi akn local entonces aumentamos 
            # nuestro akn y seguimos con el siguiente paquete:
            akn_to_writer = (akn_to_writer + 1)%1000 
        if chunk == b'':
            break

newthread.join()

print("Bytes enviados: ", bytes_sent)
print("Total de bytes enviados: ", bytes_sent_total)
print("Bytes recibidos: ", bytes_received)
print("Errores: ", errors)

s.close()