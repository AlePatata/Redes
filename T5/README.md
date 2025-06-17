# T5
## Principales changesss
- Ventana receptor: esta ventana no puede (o no sabría como implementarlo) ser como la del emisor, que la modelé literalmente como una lista de tamanno win que agregaba y sacaba elementos en sus extremos para "desplazarse", pues es más fácil de imaginar. Ahora no puedo pues habría una incoherencia entre los indices de las ventanas entre receptor y emisor, así que implementé directamente la idea del profe, tener un arreglo con 1000 casillas y 2 indices que se van moviendo, así puedo referirme a la casilla por un indice que servirá  para identificar literalmente qué ack es.
- Cola de prioridad de timeouts: eso, una pqueue de enteros que indican el indice de paquete cuya prioridad es su timeout. De esta forma para obtener el mas proximo debo simplemente sacarlo de la cola (será el menor) y chequear si debería ser retransmitido (si fue confirmado o no). Para esto definí una función aux getBestTimeout() que me saca el par [timeout, indice_paquete]















## Funciones Auxiliares:

- siguienteAck: suma 1 y saca modulo, porque me aburri de escribirlo en todos lados
- readAllWindow(func) retorn la lista inicial que corresponde a la ventana de data (separada en paquetes) para ser enviados. Notese que le paso como parametro una funcion lambda que corresponde siempre a read, lo dejé así para que tuviera en consideración el contexto donde iba a ser ejecutada pero supongo que podría simplificarse
- estaEnVentana(begin, n) verifica con la diferencia modular si el numero n está dentro del rango de la ventana considerando el ciclo

# T4
### Funciones auxiliares dentro del emisor
- updateList() agrega un nuevo ack a la lista de aks a enviar, luego quita el primer elemento para seguir teniendo el mismo tamaño de la ventana
- readNextLineAndAddToList(func) lee una nueva linea del input, la grega al final de la lista de data (paquetes) y quita el primer elemento. Se le da (como en una funcion previa) como parametro una lambda que corresponde a la funcion read.
- next() ejecuta ambas funciones que actualizan la data y los acks a enviar hasta el ultimo paquete confirmado hasta el momento (ack_to_emisor). Basicamente simula "mover la ventana"

## De tareas previas...
Se rescatan los prints y variables que llevan el conteo de bytes enviados y errores:
- Bytes enviados: bytes enviados sin repetición
- Total de bytes enviados: bytes enviados contando la repetición de algun paquete
- Bytes recibidos: bytes recibidos por el thread receptor
- Errores: cantidad de paquetes que hayan tenido que ser reenviados
Además se utiliza la misma lógica para agregar el ack al envio de cada paquete con la función format(i)

## Pruebas de exploración iniciales (con una imagen)
Igual que en las tareas anteriores se probó primero con una imagen 66807 bytes. En general este protocolo tuvo un excelente desempeño casi sin errores, como se verá a continuación...

### Local
Primero probamos con timeout de 3 segundos, size de 1024 y ventana de 10
```shell
time ./client_bw.py 1024 3 10 in.jpeg out.jpeg 127.0.0.1 1818

>> ... 
>> Trying to send package with ack: 67
>> ack received:  059
>> ack received:  060
>> Sending empty package
>> Trying to send package with ack: 68
>> ack received:  061
>> ack received:  062
>> ack received:  063
>> ack received:  064
>> ack received:  065
>> ack received:  066
>> EOF marcador
>> Bytes enviados:  291427
>> Total de bytes enviados:  291427
>> Bytes recibidos:  168681
>> Errores:  0
>> 
>> real	0m0,056s
>> user	0m0,027s
>> sys	0m0,014s
```
COmo funcionó perfecto (obvio) forzaremos los parámetrs...
```shell
time ./client_bw.py 2048 0.1 100 in.jpeg out.jpeg 127.0.0.1 1818
>> ...
>> ack received:  022
>> Sending empty package
>> Trying to send package with ack: 33
>> ack received:  023
>> ack received:  024
>> ack received:  025
>> ack received:  026
>> ack received:  027
>> ack received:  028
>> ack received:  029
>> ack received:  030
>> ack received:  031
>> ack received:  032
>> ack received:  033
>> EOF marcador
>> Bytes enviados:  186873
>> Total de bytes enviados:  186873
>> Bytes recibidos:  66909
>> Errores:  0
>> 
>> real	0m0,044s
>> user	0m0,022s
>> sys	0m0,015s
```
```shell
time ./client_bw.py 2048 0.01 500 in.jpeg out.jpeg 127.0.0.1 1818
>> ...
>> EOF marcador
>> Trying to send package with ack: 30
>> Bytes enviados:  508260
>> Total de bytes enviados:  508260
>> Bytes recibidos:  66909
>> Errores:  0
>> 
>> real	0m0,072s
>> user	0m0,013s
>> sys	0m0,041s
```
Pero cuando probé con una ventana de 1000 se cayó, pues la función de está dentro de la ventana (estaEnVentana()) tendría un comportamiento extraño pues el ack mas grande es 999. De hecho con una ventana de tamaño 999 sigue funcionando:
```shell
time ./client_bw.py 2048 0.01 999 in.jpeg out.jpeg 127.0.0.1 1818
>> ...
>> EOF marcador
>> Trying to send package with ack: 30
>> Bytes enviados:  508260
>> Total de bytes enviados:  508260
>> Bytes recibidos:  66909
>> Errores:  0
>> 
>> real	0m0,072s
>> user	0m0,013s
>> sys	0m0,041s
```
Con timeouts pequeños sigue funcionando 
```shell
time ./client_bw.py 2048 0.001 999 in.jpeg out.jpeg 127.0.0.1 1818
>> ...
>> ack received:  033
>> EOF marcador
>> Bytes enviados:  855692
>> Total de bytes enviados:  855692
>> Bytes recibidos:  66909
>> Errores:  0
>> 
>> real	0m0,057s
>> user	0m0,030s
>> sys	0m0,023s
```
Y con size más grandes
```shell
time ./client_bw.py 4096 0.001 999 in.jpeg out.jpeg 127.0.0.1 1818
>> ...
>> ack received:  017
>> EOF marcador
>> Bytes enviados:  1180181
>> Total de bytes enviados:  1180181
>> Bytes recibidos:  66861
>> Errores:  0
>> 
>> real	0m0,054s
>> user	0m0,037s
>> sys	0m0,017s
```
HAsta que falló con:
```shell
time ./client_bw.py 36000 0.001 999 in.jpeg out.jpeg 127.0.0.1 1818
>> 
>> Trying to send package with ack: 0
>> Trying to send package with ack: 1
>> Sending empty package
>> Trying to send package with ack: 2
>> ack received:  000
>> ack received:  001
>> ack received:  002
>> Timeout alcanzado en el emisor, reenviando paquetes...
>> Trying to send package with ack: 0
>> Trying to send package with ack: 1
>> Sending empty package
>> Trying to send package with ack: 2
>> Trying to send package with ack: 0
>> EOF marcador
>> Bytes enviados:  169635
>> Total de bytes enviados:  169635
>> Bytes recibidos:  66816
>> Errores:  1
>> 
>> real	0m0,054s
>> user	0m0,027s
>> sys	0m0,023s
```

En resumen...

| Tamaño (size) | Timeout | Ventana | Bytes enviados | Bytes recibidos | Errores | Tiempo (real) |
| ------------- | ------- | ------- | -------------- | --------------- | ------- | ------------- |
| 1024          | 3       | 10      | 291427         | 168681          | 0       | 0m0,056s      |
| 2048          | 0.1     | 100     | 186873         | 66909           | 0       | 0m0,044s      |
| 2048          | 0.01    | 500     | 508260         | 66909           | 0       | 0m0,072s      |
| 2048          | 0.01    | 999     | 508260         | 66909           | 0       | 0m0,072s      |
| 2048          | 0.001   | 999     | 855692         | 66909           | 0       | 0m0,057s      |



### Anakena
Con tamaños decentes...
```shell
time ./client_bw.py 1024 1 100 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  066
>> EOF marcador
>> Bytes enviados:  154035
>> Total de bytes enviados:  154035
>> Bytes recibidos:  144539
>> Errores:  0
>> 
>> real	0m0,250s
>> user	0m0,021s
>> sys	0m0,172s
```
Ventana masiva...
```shell
time ./client_bw.py 1024 1 999 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  066
>> EOF marcador
>> Bytes enviados:  132989
>> Total de bytes enviados:  132989
>> Bytes recibidos:  128881
>> Errores:  0
>> 
>> real	0m0,169s
>> user	0m0,039s
>> sys	0m0,087s
```
Con timeout pequeño tuvo 1 fallo:
```shell
time ./client_bw.py 1024 0.01 999 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  066
>> EOF marcador
>> Trying to send package with ack: 14
>> Bytes enviados:  136070
>> Total de bytes enviados:  136070
>> Bytes recibidos:  67008
>> Errores:  1
>> 
>> real	0m0,121s
>> user	0m0,012s
>> sys	0m0,062s
```
Aunque al agrandar el size se corrigió...
```shell
time ./client_bw.py 4096 1 999 in.jpeg out.jpeg anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  017
>> EOF marcador
>> Bytes enviados:  212549
>> Total de bytes enviados:  212549
>> Bytes recibidos:  120148
>> Errores:  0
>> 
>> real	0m0,125s
>> user	0m0,013s
>> sys	0m0,073s
```

En resumen...

| Tamaño (size) | Timeout | Ventana | Bytes enviados | Bytes recibidos | Errores | Tiempo (real) |
| ------------- | ------- | ------- | -------------- | --------------- | ------- | ------------- |
| 1024          | 1       | 100     | 154035         | 144539          | 0       | 0m0,250s      |
| 1024          | 1       | 999     | 132989         | 128881          | 0       | 0m0,169s      |
| 1024          | 0.01    | 999     | 136070         | 67008           | 1       | 0m0,121s      |


## Archivo más grande
Nuevamente generamos un archivo con el siguiente comando para crear un archivo de 500MB:
`dd if=/dev/zero of=put/large_in.dat bs=500M count=1 status=none`.
Probé con size bastante grandes pues para un archivo de 500MB se iba a demorar mucho con sizes como los anteriores...

### Local

```shell
time ./client_bw.py 36000 3 100 put/large_in.dat put/large_out.dat 127.0.0.1 1818
>> ...
>> ack received:  564
>> EOF marcador
>> Bytes enviados:  12131199057
>> Total de bytes enviados:  12131199057
>> Bytes recibidos:  2220161046
>> Errores:  2
>> 
>> real	0m47,020s
>> user	0m2,821s
>> sys	0m21,182s
```
Si aumentamos la ventana y disminuimos el timeout...
```shell
time ./client_bw.py 36000 1 500 put/large_in.dat put/large_out.dat 127.0.0.1 1818
>> ...
>> EOF marcador
>> Bytes enviados:  61990391794
>> Total de bytes enviados:  61990391794
>> Bytes recibidos:  11805952090
>> Errores:  2
>> 
>> real	2m38,878s
>> user	0m16,535s
>> sys	1m12,325s
```
Si aumentamos al máximo la ventana y disminuimos más el timeout...
```shell
time ./client_bw.py 36000 0.1 999 put/large_in.dat put/large_out.dat 127.0.0.1 1818
>> ...
>> EOF marcador
>> Bytes enviados:  95529273175
>> Total de bytes enviados:  95529273175
>> Bytes recibidos:  18892338529
>> Errores:  2
>> 
>> real	4m12,959s
>> user	0m29,401s
>> sys	1m51,094s
```

En resumen...

| Tamaño (size) | Timeout | Ventana | Bytes enviados | Bytes recibidos | Errores | Tiempo (real) |
| ------------- | ------- | ------- | -------------- | --------------- | ------- | ------------- |
| 36000         | 3       | 100     | 12,131,199,057 | 2,220,161,046   | 2       | 0m47,020s     |
| 36000         | 1       | 500     | 61,990,391,794 | 11,805,952,090  | 2       | 2m38,878s     |
| 36000         | 0.1     | 999     | 95,529,273,175 | 18,892,338,529  | 2       | 4m12,959s     |


### Anakena
Como se pudo apreciar en las prubas anteriores, se estaba demorando demasiado, y considerando que por lo general el local tiene mejor desempeño que anakena decidí probar con un archivo de solo 500KB
`dd if=/dev/zero of=put/large_in.dat bs=1K count=500 status=none`

```shell
 time ./client_bw.py 36000 3 100 put/large_in.dat put/large_out.dat anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  015
>> EOF marcador
>> Bytes enviados:  1328246
>> Total de bytes enviados:  1328246
>> Bytes recibidos:  1096105
>> Errores:  0
>> 
>> real	0m0,354s
>> user	0m0,025s
>> sys	0m0,268s
```

```shell
time ./client_bw.py 36000 0.1 999 put/large_in.dat put/large_out.dat anakena.dcc.uchile.cl 1818
>> ...
>> EOF marcador
>> Sending empty package
>> Trying to send package with ack: 15
>> Bytes enviados:  1684264
>> Total de bytes enviados:  1684264
>> Bytes recibidos:  1148111
>> Errores:  0
>> 
>> real	0m0,496s
>> user	0m0,088s
>> sys	0m0,416s
```

Como estos resultados fueron demasiado rápido forzaremos un poco ajustando el size
```shell
time ./client_bw.py 1024 3 100 put/large_in.dat put/large_out.dat anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  500
>> EOF marcador
>> Trying to send package with ack: 500
>> Bytes enviados:  786694
>> Total de bytes enviados:  786694
>> Bytes recibidos:  773334
>> Errores:  0
>> 
>> real	0m0,577s
>> user	0m0,040s
>> sys	0m0,440s
```
```shell
time ./client_bw.py 1024 0.01 100 put/large_in.dat put/large_out.dat anakena.dcc.uchile.cl 1818
>> ...
>> ack received:  500
>> EOF marcador
>> Bytes enviados:  898628
>> Total de bytes enviados:  898628
>> Bytes recibidos:  884250
>> Errores:  0
>> 
>> real	0m0,618s
>> user	0m0,042s
>> sys	0m0,481s
```

EN resumen...

| Tamaño (size) | Timeout | Ventana | Bytes enviados | Bytes recibidos | Errores | Tiempo (real) |
| ------------- | ------- | ------- | -------------- | --------------- | ------- | ------------- |
| 36000         | 3       | 100     | 1,328,246      | 1,096,105       | 0       | 0m0,354s      |
| 36000         | 0.1     | 999     | 1,684,264      | 1,148,111       | 0       | 0m0,496s      |
| 1024          | 3       | 100     | 786,694        | 773,334         | 0       | 0m0,577s      |
| 1024          | 0.01    | 100     | 898,628        | 884,250         | 0       | 0m0,618s      |



## Conclusiones
Los resultados de las pruebas de este protocolo me sorprendieron pues son muy versatiles y flexibles, de forma que es dificil que falle de manera incomprensible, con esto me refiero al error del tamaño de la ventana superior al de la cantidad de acks posibles. 

### Respuesta a las preguntas pasadas


1. Si el archivo de salida es más pequeño que el de entrada, ¿puede ocurrir aunque mi protocolo esté bien implementado?

Igualmente como en la tarea anterior...
No es correcto, pero esta vez es mucho más improbable pues el protocolo de GO-Back-N es más robusto frente a pérdidas de paquetes. En la tarea pasada se podía dar el caso que al haber retransmisiones se acumularan los paquetes en el de salida y terminara teniendo un tamaño mayor al de entrada. Esta vez esos paquetes que se adelantan o llegan "doble" se escribirán 1 vez en el archivo de salida.

2. Los valores de ancho de banda medidos en esta tarea son muy distintos a los de la T1 y T2. ¿cuál es la causa principal de estas diferencias?

La causa principal es este protocolo incluye confirmación por ACK, ventana de control de flujo, y temporización, lo que introduce overhead. Aun así, cuando se ajustan correctamente los parámetros (por ejemplo, size y ventana grandes, timeout pequeño pero manejable), se logra un rendimiento significativamente mejor. En local, obtuve tiempos reales de menos de 0.06s incluso con archivos de más de 60KB. En Anakena, aunque la latencia es mayor, el uso de una ventana amplia ayudó a mantener el flujo sin pausas, mejorando el ancho de banda respecto a Stop-and-Wait. Sin embargo, en condiciones extremas o mal calibradas (ventana muy grande, timeout muy pequeño), puede haber retransmisiones innecesarias y errores, afectando negativamente el rendimiento, aunque aqui no se dió el caso.

3. Dijimos que un protocolo bien implementado no debiera nunca morir por el timeout de 3 segundos puesto en el socket de recepción. ¿Por qué es esto así?

Igualmente como en la tarea anterior...
El timeout de 3 segundos es un "límite de seguridad" y no es una parte activa del protocolo, es decir, ese timeout solo se alcanzará cuando haya un error externo al protocolo en sí. Es utilizado como medida de precaución para evitar que el thread receptor quede bloqueado indefinidamente si no recibe datos o confirma el último paquete en el tiempo esperado. Sin embargo, en nuestro caso la confirmación de los paquetes se hace de manera muy rápida pues no se envía nada a través del socket, si no que se modifica una variable global. AL disminuir el timeout obtuvimos errores pero estos están relacionados a retrasos en el envío del paquete más que a su pérdida. De hecho no tuvimos ninguna pérdida de paquetes, más bien retrasos que conllevaron a un reenvío de ciertos paquetes y sus dobles recepciones en el archivo de salida.