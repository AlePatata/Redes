#!/usr/bin/python3
# Echo client program
import jsockets
import sys, threading
from threading import Lock, Condition, Event
import socket as socket 
import time # Para obtener hora envio y recepcion
import queue # Para guardar los timeuts ordenados por proximidad

# Variables globalesss
mutex_lock = Lock()
condition = Condition()
done_event = Event()

errors = 0
packets = 0       # Without resending packages
total_packets = 0 # Counting the re-sent packages
bytes_received = 0
ack_to_emisor = [-1 for i in range(1000)]
last_confirmed = -1 # Ultimo ack confirmado
higher_confirmed = -1 # Paquete más a la derecha recibido(considerando ciclo), para el cálculo de max_win
max_win = 0
horas_de_envio = queue.PriorityQueue()
horas_de_recepción = []
prom_tiempo = 0

### Funciones Auxiliaresss
def format(i):
  return str(i).zfill(3).encode

def readAllWindow(func):  
  return [func(size) or b'' for _ in range(win)]

def estaEnVentana(begin, n):
  return (n - begin + 1000) % 1000 < win

# Dada una ventana, agrega un elemento al final y quita el primero
def updateList(ventana, new_element):
    ventana.append(new_element) # Agregar uno al final de la ventana
    ventana.pop(0) # Sacar el primero en la ventana

def siguienteAck(n):
  return (n+1)%1000

# Receptor
def Rdr(s):
  global bytes_received, ack_to_emisor, last_confirmed, timeout
  expected = 0
  s.settimeout(timeout)
  eof = False
  window_data = [None for i in range(win)] # Rellenamos con placeholders


  with open(outp, 'wb') as outfile:

    def writeNextChunk(): # Mueve la ventana del receptor (ack_to_emisor)
      global window_data
      outfile.write(window_data[0]) # Escribir
      window_data.pop(0) # Quita el primer chunk en la ventana de data
      window_data.append(-1) # Y agrega un elemnto que hace de placeholder para guardar otro chunk


    def moveWindowAndWriteData(): # Mueve la ventana del receptor (ack_to_emisor)
      global last_confirmed, expected
      while ack_to_emisor[0] == siguienteAck(last_confirmed): # Si el primero es un aumento de lo último que recibió
        last_confirmed = ack_to_emisor[0]
        updateList(ack_to_emisor, None) # Agregamos un placeholder
        writeNextChunk()
      expected = siguienteAkn(last_confirmed)


    while not eof:
      try:
        total_data = s.recv(size + 3)
        bytes_received += len(total_data)
        data = total_data[3:]
        ack_received_bytes = total_data[:3]
        ack_received = int(ack_received_bytes.decode())
        print("ack received: ", ack_received)

        with condition:
          if estaEnVentana(expected, ack_received):
            if expected == ack_received: 
              if data == b'':
                with mutex_lock:
                  print("EOF marcador")
                  done_event.set()
                  condition.notify_all()
                eof = True
                break
              else:
                with mutex_lock:
                  moveWindowAndWriteData()
            
            # Obtenemos el indice del paquete recibido en nuestra ventana
            index = (ack_received - expected + 1000)%1000 # diferencia modular
            window_data[index] = data # guardamos el package
            with mutex_lock:
              ack_to_emisor[index] = ack_received # marcamos como recibido
              moveWindowAndWriteData() # Si se puede movemos la ventana (no estoy segura si hará algojdfshfs)
            condition.notify()
          
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
  ack_to_emisor = [-1 for i in range(win)]  # Inicializamos ventana de receptor en -1's
  window_data = readAllWindow(lambda _: infile.read(_)) # Ventanita de packages
  windows_recieved = 0 # Variable para determinar cuantos paquetes faltan 

  def readNextLineAndAddToList(func): 
    global window_data
    window_data.pop(0) # Quita el primer chunk en la ventana de data
    last_chunk = func(size)
    if not last_chunk:
      last_chunk = b''
    window_data.append(last_chunk) # Y agrega uno nuevo que puede ser vacio

  def moveWindowAndData():
    global last_confirmed
    first_one = ack_to_receptor[0]
    for i in range((last_confirmed + 1 - first_one+1000)%1000): # diferencia modular
      updateList(ack_to_receptor, (ack_to_receptor[-1]+1)%1000)
      readNextLineAndAddToList(lambda _: infile.read(size))

  def getBestTimeout():
    while not horas_de_envio.empty():
      t = horas_de_envio.queue[0][0] # Obtenemos el mejor timeout
      index = horas_de_envio.get() # Sacamos el indice de ese paquete
      ack_correspondiente = ack_to_receptor[index]
      with mutex_lock:
        # Si el proximo timeout es de un paquete no confirmado
        if ack_to_emisor[ack_correspondiente-1] != ack_correspondiente:
          return t, index
    # Si se acabó la cola, todos estaban confirmados. no deberíamos llegar a este caso
    return -1, -1

    
  while True:
    with mutex_lock:
      if done_event.is_set():
        break 

    with condition:
      with mutex_lock:
        # Si se puede avanzamos la ventana
        moveWindowAndData() 

      while windows_recieved != win: # Mientras falten paquetes por recibir # cond protege datarace(?
        proximo_timeout, index = getBestTimeout()
        if proximo_timeout < time.time():
          print("Timeout alcanzado por el package ", index+1, " reenviando...")
          errors += 1
          try:
            new_timeout = time.time()
            horas_de_envio.put((timeout, index)) # Actualizamos tiempo del que sacamos
            s.send(window_data[index])
          except error:
            print("Error al enviar el paquete ", index)
            continue
        else:
          # Si se cumplió que la variable global es la misma que mi ack local (el primero en la lista) 
          # entonces avanzamos la ventana:  
          with mutex_lock:
            moveWindowAndData()
    

newthread.join()
s.close()

print("sent ", packets, "packets,")
print("retrans ", errors, ",")
print("tot packs ", total_packets, ",")
print(errors/total_packets, "%")
print("Max_win: ", max_win)
print("rtt est = ", )
