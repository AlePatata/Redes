#!/usr/bin/python3
# Echo client program
import jsockets
import sys, threading
from threading import Lock, Condition, Event
import socket as socket 

# Variables globalesss
mutex_lock = Lock()
condition = Condition()
done_event = Event()

errors = 0
bytes_sent = 0       # Without resending packages
bytes_sent_total = 0 # Counting the re-sent packages
bytes_received = 0
ack_to_emisor = -1

### Funciones Auxiliaresss
def format(i):
  return str(i).zfill(3).encode()

def sendPackage(chunk, ack):
  global bytes_sent, bytes_sent_total
  if not chunk:
    chunk = b''
    print(f'Sending empty package')
  print(f'Trying to send package with ack: {ack}')
  byte_array_ack = format(ack)
  increment = s.send(byte_array_ack+chunk)
  bytes_sent += increment
  bytes_sent_total += increment

def readAllWindow(func):  
  return [func(size) or b'' for _ in range(win)]

def estaEnVentana(begin, n):
  return (n - begin + 1000) % 1000 < win

def sendAll(window_data, ack_to_receptor):
  empty = False
  for i in range(win): # Enviamos toda la ventana
    if empty:
      return
    with mutex_lock:
      if done_event.is_set():
        return
    sendPackage(window_data[i], ack_to_receptor[i])
    if not window_data[i] or window_data[i] == b'':
      empty = True # No vale la pena seguir enviando paquetes vacíos



# Receptor
def Rdr(s):
  global bytes_received, ack_to_emisor
  expected = 0
  last_received = -1
  s.settimeout(15)
  with open(outp, 'wb') as outfile:
    while True:
      try:
        total_data = s.recv(size + 3)
        bytes_received += len(total_data)
        data = total_data[3:]
        ack_received_bytes = total_data[:3]
        ack_received = ack_received_bytes.decode()
        print("ack received: ", ack_received)
        with condition:
          if expected == int(ack_received): 
            outfile.write(data)
            last_received = expected
            expected = (expected+1)%1000
            
            if data == b'':
              with mutex_lock:
                print("EOF marcador")
                done_event.set()
                condition.notify_all()
              break
          with mutex_lock:
            ack_to_emisor = last_received
          condition.notify_all()
          
      except socket.timeout:
        print("Timeout alcanzado en receptor")
        with mutex_lock:
          done_event.set()
        break

# Input
if len(sys.argv) != 8:
  print('Use: '+sys.argv[0]+' size windows timeout input output host port')
  sys.exit(1)

size = int(sys.argv[1])
timeout = float(sys.argv[2])
win = int(sys.argv[3])
inp = sys.argv[4]
outp = sys.argv[5]
host = sys.argv[6]
port = sys.argv[7]

s = jsockets.socket_udp_connect(host, port)
if s is None:
  print('could not open socket')
  sys.exit(1)

newthread = threading.Thread(target=Rdr, args=(s,))
newthread.start()

# Emisor
with open(inp, 'rb') as infile:
  ack_to_receptor = [i for i in range(win)]
  window_data = readAllWindow(lambda _: infile.read(_))

  def updateList():
    global ack_to_receptor
    ack_to_receptor.append((ack_to_receptor[-1]+1)%1000)
    ack_to_receptor.pop(0)

  def readNextLineAndAddToList(func):
    global window_data
    window_data.pop(0)
    last_chunk = func(size)
    if not last_chunk:
      last_chunk = b''
    window_data.append(last_chunk)

  def next():
    global ack_to_emisor
    first_one = ack_to_receptor[0]
    for i in range((ack_to_emisor + 1 - first_one+1000)%1000): # diferencia modular
      updateList()
      readNextLineAndAddToList(lambda _: infile.read(size))   
    
  while True:
    with mutex_lock:
      if done_event.is_set():
        break
    
    sendAll(window_data, ack_to_receptor)

    with condition:
      with mutex_lock:
        # Si se puede avanzamos la ventana
        while estaEnVentana(ack_to_receptor[0], ack_to_emisor):
          next()

      while not estaEnVentana(ack_to_receptor[0], ack_to_emisor) and not ack_to_receptor[0]:
        if not condition.wait(timeout=timeout):
          print("Timeout alcanzado en el emisor, reenviando paquetes...")
          errors += 1
          sendAll(window_data, ack_to_receptor)
        else:
          # Si se cumplió que la variable global es la misma que mi ack local (el primero en la lista) 
          # entonces avanzamos la ventana:  
          with mutex_lock:
            while estaEnVentana(ack_to_receptor[0], ack_to_emisor):
              next()
    

newthread.join()
s.close()

print("Bytes enviados: ", bytes_sent)
print("Total de bytes enviados: ", bytes_sent_total)
print("Bytes recibidos: ", bytes_received)
print("Errores: ", errors)
