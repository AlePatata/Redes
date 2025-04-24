# T2
Arreglé mi código de la T1 (espero que bien) y realicé tests un poco más simples, dejando un resumen acá. Mi cliente también cuenta bytes recibidos y enviados y un marcador cuando finaliza el cual puede ser "EOF marcador" o "Timeout alcanzado" 

## Pruebas iniciales de exploraciónprimero con una imagen con:
### Local
```shell
time ./client_bw.py 1024 in.jpeg out.jpeg 127.0.0.1 1818
>> EOF marcador
>> Bytes enviados:  66807
>> Bytes recibidos:  66807
>>
>> real	0m0,043s
>> user	0m0,020s
>> sys	0m0,021s
```
Lo que fue exitoso hasta reducir size hasta 256 que ya mostró el primer timeout
```shell
time ./client_bw.py 256 in.jpeg out.jpeg 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  66807
>> Bytes recibidos:  42752
>> 
>> real	0m3,079s
>> user	0m0,040s
>> sys	0m0,006s
```
### Anakena

```shell
time ./client_bw.py 1024 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> EOF marcador
>> Bytes enviados:  66807
>> Bytes recibidos:  66807
>> 
>> real	0m0,099s
>> user	0m0,006s
>> sys	0m0,041s
```
Continuó con un rendimiento similar hasta que falló en size 64:
```shell
time ./client_bw.py 64 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> Timeout alcanzado
>> Bytes enviados:  66807
>> Bytes recibidos:  44928
>> 
>> real	0m3,284s
>> user	0m0,021s
>> sys	0m0,093s
```


## Archivo grande
Para crear un archivo grande utilizé `dd if=/dev/zero of=put/large_local_in.dat bs=500M count=1 status=none`
### Local
Para el archivo grande probé fallidamente con tamaños de 
- 16384:
```shell
time ./client_bw.py 16384 put/large_local_in.dat put/large_local_out.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  524288000
>> Bytes recibidos:  242073600
>> 
>> real	0m6,592s
>> user	0m0,067s
>> sys	0m3,214s
```
- 32768:
```shell
time ./client_bw.py 32768 put/large_local_in.dat put/large_local_out.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  524288000
>> Bytes recibidos:  8519680
>> 
>> real	0m3,270s
>> user	0m0,051s
>> sys	0m0,201s
```
- Y 65536 pero el código no lo permitió...
```shell
time ./client_bw.py 65536 put/large_local_in.dat put/large_local_out.dat 127.0.0.1 1818
Traceback (most recent call last):
  File "/home/pss/Escritorio/Redes/T2/./client_bw.py", line 56, in <module>
    bytes_sent += s.send(chunk)
                  ^^^^^^^^^^^^^
OSError: [Errno 90] Message too long
Timeout alcanzado

real	0m3,031s
user	0m0,019s
sys	0m0,010s
```
Así que amplié el timeout a 100 segundos para ver en realidad cuánto le habría tomado enviar esos 500MB, pero tuvo demasiadas pérdidas de paquetes:
```shell
time ./client_bw.py 32768 put/large_local_in.dat put/large_local_out.dat 127.0.0.1 1818
>> EOF marcador
>> Bytes enviados:  524288000
>> Bytes recibidos:  72220672
>> 
>> real	0m0,629s
>> user	0m0,058s
>> sys	0m0,341s
```
Un segundo intento tampoco mejoró aunque usó todo su tiempo
```shell
time ./client_bw.py 32768 put/large_local_in.dat put/large_local_out.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  524288000
>> Bytes recibidos:  41385984
>> 
>> real	1m40,486s
>> user	0m0,034s
>> sys	0m0,308s
```
### Anakena
Similarmente, la pérdida de paquetes fue demasiada
```shell
time ./client_bw.py 32768 put/large_local_in.dat put/large_local_out.dat anakena.dcc.uchile.cl 1818
>> Timeout alcanzado
>> Bytes enviados:  524288000
>> Bytes recibidos:  89653248
>> 
>> real	0m34,034s
>> user	0m0,151s
>> sys	0m28,509s
```

## 100 Archivos paralelos
Los resultados a continuación se pueden repetir usando el código shell en test/small_files.sh y modificando los parámetros en su encabezado
Primero probé con 1 proceso, que correría el cliente y para un archivo de 5MB intetaría con sizes 1024, 4096 y 32768 en local y anakena. Fracasó...
```shell
./test/small_files_1024.sh 
>> Tamaño de buffer: 1024 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 1024 put/smalls_in/file_1.dat put/smalls_out/file_1.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  563200
>> Duración test: 3.096170000
>> Tamaño de buffer: 4096 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 4096 put/smalls_in/file_1.dat put/smalls_out/file_1.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  221184
>> Duración test: 3.051350326
>> Tamaño de buffer: 32768 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 32768 put/smalls_in/file_1.dat put/smalls_out/file_1.dat 127.0.0.1 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  851968
>> Duración test: 3.044406767
>> Tamaño de buffer: 1024 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 1024 put/smalls_in/file_1.dat put/smalls_out/file_1.dat anakena.dcc.uchile.cl 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  548864
>> Duración test: 3.403852186
>> Tamaño de buffer: 4096 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 4096 put/smalls_in/file_1.dat put/smalls_out/file_1.dat anakena.dcc.uchile.cl 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  876544
>> Duración test: 3.391221212
>> Tamaño de buffer: 32768 bytes
>> Generando 1 archivos pequeños (5MB cada uno)...
>> running ./client_bw.py 32768 put/smalls_in/file_1.dat put/smalls_out/file_1.dat anakena.dcc.uchile.cl 1818
>> Timeout alcanzado
>> Bytes enviados:  5242880
>> Bytes recibidos:  1114112
>> Duración test: 3.379366264
>> Pruebas completadas. Resultados en test/small_results.md
```

Así que disminuí el tamaño de los archivos a 1MB y probé con 10 procesos. El resultado en anakena con size 32768 fue:
```shell
>> EOF marcador
>> Bytes enviados:  1048576
>> Bytes recibidos:  196608
>> EOF marcador
>> Bytes enviados:  1048576
>> Bytes recibidos:  32768
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  0
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  0
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  98304
>> Timeout alcanzado
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  65536
>> Bytes enviados:  1048576
>> Bytes recibidos:  65536
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  32768
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  65536
>> Timeout alcanzado
>> Bytes enviados:  1048576
>> Bytes recibidos:  131072
>> Duración test: 3.488388934
>> Pruebas completadas. Resultados en test/small_results.md
```
Lo que sigue siendo malo pues solo 2 alcanzaron EOF y tuvieron pérdidas de paquetes. Probé con archivos de tamaño 100 KB:
### Anakena size 32768
```shell
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  65536
>> EOF marcador
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  32768
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  0
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  0
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  32768
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  32768
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  98304
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  98304
>> Duración test: 3.350801414
>> Pruebas completadas. Resultados en test/small_results.md
```
### Local size 4096
```shell
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> EOF marcador
>> Bytes enviados:  102400
>> Bytes recibidos:  102400
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  95232
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  95232
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  95232
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  95232
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  49152
>> Timeout alcanzado
>> Bytes enviados:  102400
>> Bytes recibidos:  49152
>> Duración test: 3.222379447
```
## Resultados generales
Puede ver todos los resultados de las pruebas paralelas de 100 archivos en test/results.txt y repetirlas con `./test/small_files.sh >> test/results.txt` donde finalmente probé con archivos de tamaño 100KB y sizes de lectura de 4096 y 32768, para local y anakena

 # Conclusiones

| Tamaño de Buffer | Entorno          | Archivos | Éxitos Completos | Éxitos Parciales | Fallos | Duración Promedio (s) | Tasa de Éxito (%) | Throughput Promedio (KB/s) |
|------------------|------------------|----------|-------------------|-------------------|--------|------------------------|--------------------|-----------------------------|
| 1024 bytes       | localhost        | 10       | 2                 | 6                 | 2      | 3.17                   | 20%                | 32.3                        |
| 4096 bytes       | localhost        | 10       | 8                 | 1                 | 1      | 3.21                   | 80%                | 319.0                       |
| 32768 bytes      | localhost        | 10       | 8                 | 1                 | 1      | 3.14                   | 80%                | 326.1                       |
| 1024 bytes       | anakena.dcc...   | 10       | 4                 | 3                 | 3      | 3.53                   | 40%                | 29.0                        |
| 4096 bytes       | anakena.dcc...   | 10       | 7                 | 2                 | 1      | 3.36                   | 70%                | 304.8                       |
| 32768 bytes      | anakena.dcc...   | 10       | 6                 | 3                 | 1      | 3.24                   | 60%                | 316.0                       |
| 4096 bytes       | localhost        | 100      | 94                | 5                 | 1      | 4.72                   | 94%                | 216.9                       |
| 32768 bytes      | localhost        | 100      | 98                | 1                 | 1      | 4.65                   | 98%                | 220.2                       |
| 4096 bytes       | anakena.dcc...   | 100      | 70                | 24                | 6      | 5.59                   | 70%                | 183.2                       |
| 32768 bytes      | anakena.dcc...   | 100      | 80                | 15                | 5      | 5.18                   | 80%                | 197.7                       |

 
 1. Si el archivo de salida es más pequeño que el de entrada, ¿es correcto medir el ancho de banda disponible como tamaño recibido / tiempo?
No es correcto. Medir el ancho de banda como tamaño recibido / tiempo solo es válido si todo el archivo fue recibido correctamente.
Si el archivo de salida es más pequeño que el de entrada, eso indica una transferencia incompleta (posiblemente por error o corte prematuro), lo que invalida la medición porque no refleja la velocidad real de transmisión, sino una transmisión parcial.

2. Si el archivo de salida es más pequeño que el de entrada, ¿es correcto medir el ancho de banda disponible como tamaño enviado / tiempo?
Tampoco es correcto. Aunque el cliente haya enviado todo el archivo, si el servidor no recibió todo, entonces el canal de comunicación no fue capaz de sostener ese flujo completo. Usar el tamaño enviado para calcular el ancho de banda en este caso sobrestima la capacidad real.

3. Una medición que termina por timeout, ¿podría usarse de alguna forma para medir el ancho de banda disponible?
Se puede usar como una estimación inferior, pero no como una medición precisa del ancho de banda disponible. Al terminar por timeout indica que la transferencia no se completó. Aun así, se podría estimar un ancho de banda parcial usando el tamaño efectivamente transferido antes del timeout dividido por el tiempo transcurrido.

Esto puede ser útil como una aproximación inferior del ancho de banda, pero no es confiable como una medición precisa porque:

- El timeout pudo deberse a congestión, latencia alta, o fallas.

- No sabemos si la velocidad de transferencia fue constante.