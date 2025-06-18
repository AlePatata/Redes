#!/usr/bin/python3
import jsockets
import sys, threading
from threading import Lock, Condition, Event
import socket as socket 
import queue # Para guardar los timeuts ordenados por proximidad
from datetime import datetime, timedelta # Para obtener hora envio y recepcion
from aux_functions import *

mutex_lock = Lock()
condition = Condition()
done_event = Event()

# Variables globalesss
errors = 0
packets = 0       # Without resending packages
total_packets = 0 # Counting the re-sent packages
ack_to_emisor = [-1 for i in range(1000)]
last_confirmed = -1 # Ultimo ack confirmado
horas_de_envio = queue.PriorityQueue()
horas_de_recepción = [None for i in range(1000)]
prom_tiempo = 0
little_timeout = 1
rtt_estimado = None


# Receptor
def Rdr(s):
  global ack_to_emisor, last_confirmed, timeout, horas_de_recepción
  expected = 0               # Primer paquete que se espera
  eof = False                # Señal de fin de archivo
  window_data = [None for _ in range(1000)]
  recibido = [False for _ in range(1000)]

  with open(outp, 'wb') as outfile:
    while not eof:
      try:
        total_data = s.recv(size + 3)
        t = datetime.now()
        data = total_data[3:]
        ack = int(total_data[:3].decode())

        with condition:
          if estaEnVentana(expected, ack, win):
            if horas_de_recepción[ack] is None:
              horas_de_recepción[ack] = datetime.now()
            if ack == expected:
              if len(data) == 0:
                print(f"EOF recibido en {ack}")
                eof = True
                done_event.set()
                condition.notify_all()
                break
              else:
                  # Escribir paquete esperado
                  outfile.write(data)
                  recibido[ack] = True
                  ack_to_emisor[ack] = ack
                  print("Packet recieved ", ack)
                  window_data[ack] = None  # No es necesario guardar

                  # Avanzar ventana mientras haya paquetes recibidos pendientes
                  next_ack = siguienteAck(ack)
                  while recibido[next_ack]:
                    if window_data[next_ack] == b'':
                      print("EOF al avanzar ventana")
                      eof = True
                      done_event.set()
                      condition.notify_all()
                      break
                    outfile.write(window_data[next_ack])
                    recibido[next_ack] = False
                    ack_to_emisor[next_ack] = -1
                    window_data[next_ack] = None
                    expected = next_ack
                    next_ack = siguienteAck(expected)

                  last_confirmed = expected
                  expected = siguienteAck(last_confirmed)

            else:
              # Está en la ventana pero fuera de orden
              window_data[ack] = data
              recibido[ack] = True
              ack_to_emisor[ack] = ack
              print(f"Almacenado fuera de orden: {ack}")

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
  ack_to_receptor = [i for i in range(1000)]
  window_data = [None for i in range(1000)]
  first_in_window = 0 # Primer packet EN la ventana
  for i in range(win):
    window_data[i] = infile.read(size) # Ventanita de packages



  def moveWindowAndSendData():
    global last_confirmed, first_in_window, packets, total_packets
    while distanciaBetween(first_in_window, siguienteAck(last_confirmed)) > 0:
      newPacket = siguienteAck(first_in_window,win)
      chunk = infile.read(size) # Leemos siguiente
      if not chunk:
        chunk = b''
      window_data[newPacket] = chunk
      window_data[first_in_window] = None # Limpiamos el primero
      first_in_window = siguienteAck(first_in_window) # Avanzamos la ventana
      
      # Envio del nuevo paquete
      byte_array_ack = format(newPacket)
      print("Sending the packet ", newPacket)
      b = s.send(byte_array_ack + chunk)
      timeout_time = datetime.now() + timedelta(seconds=little_timeout)
      horas_de_envio.put((timeout_time, newPacket))
      packets += 1
      total_packets += 1
      

  def getBestTimeout():
    global rtt_estimado, little_timeout
    while not horas_de_envio.empty():
      t_envio, index = horas_de_envio.get()
      with mutex_lock:
        if ack_to_emisor[index] != index:
          return (t_envio, index)  # no ha sido confirmado, es candidato a retransmisión
        elif horas_de_recepción[index] is not None:
          rtt_sample = (horas_de_recepción[index] - (t_envio - timedelta(seconds=little_timeout))).total_seconds()
          if rtt_estimado is None:
            rtt_estimado = rtt_sample
          else:
            rtt_estimado = 0.5 * rtt_estimado + 0.5 * rtt_sample
    return (-1, -1)

  for i in range(win):
    byte_array_ack = format(i)
    print("Sending the packet ", i)
    timeout_time = datetime.now() + timedelta(seconds=little_timeout)
    s.send(byte_array_ack + window_data[i])
    horas_de_envio.put((timeout_time, i))
  packets += win
  total_packets += win

  while True:
    with mutex_lock:
      if done_event.is_set():
        break 

    with condition:
      with mutex_lock:
        # Si se puede avanzamos la ventana
        moveWindowAndSendData() 

      (proximo_timeout, index) = getBestTimeout()

      if index == -1:  # Aun no hay nada en la cola, pero no terminamos
        with mutex_lock:
          moveWindowAndSendData()
        continue

      time_diff = (datetime.now() - proximo_timeout).total_seconds()
      if time_diff > 0:
        print("Timeout alcanzado por el package ", index, " reenviando...")
        errors += 1
        try:
          new_timeout = datetime.now() + timedelta(milliseconds=little_timeout)
          horas_de_envio.put((new_timeout, index)) # Actualizamos tiempo del que sacamos
          byte_array_ack = format(index)
          s.send(byte_array_ack + window_data[index])
        except Exception as e:
          print("Error al enviar el paquete ", index, ": ", e)
          continue
      else:
        # Si se cumplió que la variable global es la misma que mi ack local 
        # entonces avanzamos la ventana:  
        with mutex_lock:
          moveWindowAndSendData()

newthread.join()
s.close()

print("sent ", packets, "packets,")
print("retrans ", errors, ",")
print("tot packs ", total_packets, ",")
print(errors/total_packets, "%")
print("Max_win: ", win)
print("rtt est = ", rtt_estimado)