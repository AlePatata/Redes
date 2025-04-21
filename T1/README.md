# Tarea 1 REDES
## Cliente
Lo importante de esta tarea (el cliente) se llamó `client_bw.py` siguiendo el ejemplo del enunciado, que recibe un size, un host y un port, además de darle un archivo de entrada y otro de salida. Este cliente se hizo a partir de `client_echo3.py` solo que se quitaron los encodes y decodes, además de reemplazar las entradas y salidas estandar (prints) por los parametros recibidos. Le quité el tiempo de espera de 3 segundos al final, además del close, pues en cambio se entierra a los threads.

## Tests
Las pruebas se automatizaron (con ayuda de deepseek) en los archivos .sh de la carpeta test. Para correrlos de nuevo solo se debe asegurar de que tienes los permisos (`chmod +x test/<archivo>.sh`) y ejecutarlos con `./test/<archivo>.sh`.

Los test son:
- `large_file.sh`: Crea un archivo binario .dat de 500MB en la carpeta `put/` y prueba enviarlo por el localhost y por anakena con tamaños de lectura/escritura de 1024, 4096 y 8192. Tarda como 3 minutos y deja los resultados en `test/results.txt`. Cabe destacar que ninguna de estas pruebas, tanto variando el host o el tamaño del buffer, pudo enviar el erchivo completo, trasladando finalmente entre 505 a 518 MB, en vez de los exactos 524800 Bytes. Esto se puede ver además en la shell del server con este error
```
Cliente Conectado
Exception in thread Thread-12:
Traceback (most recent call last):
  File "/usr/lib/python3.11/threading.py", line 1038, in _bootstrap_inner
    self.run()
  File "/home/pss/Escritorio/Redes/T1/server_echo4.py", line 18, in run
    self.sock.send(data)
ConnectionResetError: [Errno 104] Connection reset by peer

```
- `small_files_1024.sh`: Crea 100 archivos binarios de 5MB cada uno en la carpeta `put/smalls_in/` y una función a la que pueden acceder 100 threads paralelamente con `-xargs`. Deja los resultados en `test/smalls_results_1024.txt`. Envía los archivos con un tamaño lectura/escritura de 1024 y los deja en `put/smalls_out/`
- `small_files_4096.sh`: Hace lo mismo que el test anterior pero con tamaño de lectura/escritura de 4096. Deja los resultados en `test/smalls_results_4096.txt`