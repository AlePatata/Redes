# T3
Para esta tarea además de la lógica STOP-AND-WAIT solicitada incluí dentro del ciclo el último mensaje vacío que hace de marcador EOF, esto por si se pierde. Este caso se diferencia de los demás al dejar en la terminal un "Sending EOF message with AKN:" con el numero del akn correspondiente, en cambio cuando no es un EOF se imprime simplemente "Trying to send package with AKN:". Además para contrastar la posible diferencia entre bytes enviados con y sin re-envio se imprime al final del script 
- Bytes enviados: bytes enviados sin repetición
- Total de bytes enviados: bytes enviados contando la repetición de algun paquete
- Bytes recibidos: bytes recibidos por el thread receptor
- Errores: cantidad de paquetes que hayan tenido que ser reenviados


## Pruebas de exploración iniciales (con una imagen)
Se le dieron los parámetros de timeout 3 y un input llamado in.jpeg que corresponde a una imagen de 66807 bytes
### Local
```shell
time ./client_bw.py 1024 3 in.jpeg out.jpeg 127.0.0.1 1818
>> Trying to send package with AKN: 000
>> AKN received:  000
>> Trying to send package with AKN: 001
>> AKN received:  001
...
>> Trying to send package with AKN: 065
>> AKN received:  065
>> Sending EOF message with AKN: 066
>> AKN received:  066
>> EOF marcador
>> Bytes enviados:  67008
>> Total de bytes enviados:  67008
>> Bytes recibidos:  67008
>> Errores:  0
>> 
>> real	0m3,056s
>> user	0m0,023s
>> sys	0m0,024s
```
En este caso no se obtuvo ningun error y la diferencia de bytes enviados con respecto al tamaño de la imagen corresponde a la cantidad de paquetes enviados (67 contando uno vacío) por los bytes añadidos en cada prefijo de 3 digitos. De hecho la tasa de paquetes pérdidos fue extremadamente baja incluso al bajar el size hasta 1 byte, donde se pudieron ver varios ciclos de 1000 prefijos enviados:
```shell
>> Bytes enviados:  267231
>> Total de bytes enviados:  267231
>> Bytes recibidos:  267231
>> Errores:  0
>> 
>> real	0m14,018s
>> user	0m1,801s
>> sys	0m2,217s
```
### Anakena
En anakena se obtuvo un resultado muy similar, donde finalmente se imprimió en la terminal el resultado para size 1024:
```shell
>> ...
>> Bytes enviados:  67008
>> Total de bytes enviados:  67008
>> Bytes recibidos:  67008
>> Errores:  0
>> 
>> real	0m3,547s
>> user	0m0,017s
>> sys	0m0,050s
```
Probé otros tamaños de lectura/escritura, mayores como 4096 u 8192 no tuvieron problemas, hasta que llegó a un error recién a los 256 bytes:
```shell
...
>> AKN received:  271
>> EOF marcador
>> Bytes enviados:  67593
>> Total de bytes enviados:  70183
>> Bytes recibidos:  71996
>> Errores:  10
>> 
>> real	0m5,198s
>> user	0m0,031s
>> sys	0m0,132s
```

## Archivo grande


### Local
Para crear un archivo grande de 500 MB utilizé `dd if=/dev/zero of=put/large_in.dat bs=500M count=1 status=none`
No hubieron errores para el caso de size 1024 y timeout 3
```shell
>> EOF marcador
>> Bytes enviados:  525824003
>> Total de bytes enviados:  525824003
>> Bytes recibidos:  525824003
>> Errores:  0
>> 
>> real	1m46,397s
>> user	0m9,252s
>> sys	0m29,257s
```
Se probó también tamaños de 8192 y 32768 y timeout de 0.1 y 0.01 sin errores.
La primera combinación en tener fallas fue size 32768 y timeout 0.001, con los siguientes resultados:
```shell
>> EOF marcador
>> Bytes enviados:  524336003
>> Total de bytes enviados:  585683315
>> Bytes recibidos:  585683315
>> Errores:  1872
>> 
>> real	0m8,884s
>> user	0m0,364s
>> sys	0m4,122s
```
Podemos notar que este resultado acumuló los paquetes recibidos, ya que el archivo resultante "large_out.dat" quedó con un peso de 585,629,696 bytes, superior a los 524.3 MB reales del archivo de input pero coherentes con la cantidad de paquetes totales enviados.

### Anakena
Se creó otro archivo pero con 500KB con `dd if=/dev/zero of=put/large_in.dat bs=1K count=500 status=none`
Luego probamos con size 1024 y timeout 3
```shell
Bytes enviados:  513503
Total de bytes enviados:  513503
Bytes recibidos:  522746
Errores:  0

real	0m7,125s
user	0m0,062s
sys	0m0,234s
```
Con size 8192 timeout 3 obtuvimos el mismo resultado sin errores:
```shell
>> Bytes enviados:  512192
>> Total de bytes enviados:  512192
>> Bytes recibidos:  512192
>> Errores:  0
>> 
>> real	0m3,823s
>> user	0m0,014s
>> sys	0m0,107s
```
Al bajar el timeout a 0.01 con size 1024 obtuvimos los primeros errores de stop-and-wait
```shell
>> Bytes enviados:  513503
>> Total de bytes enviados:  726092
>> Bytes recibidos:  728146
>> Errores:  207
>> 
>> real	0m5,101s
>> user	0m0,080s
>> sys	0m0,329s
```
En este caso el archivo de salida quedó con tamaño de 726K bytes, lo que de nuevo muestra que se acumularon los paquetes enviados.
Al mantener ese timeout y aumentar el size aumentaron los errores
```shell
>> Bytes enviados:  512753
>> Total de bytes enviados:  1261368
>> Bytes recibidos:  1261368
>> Errores:  365
>> 
>> real	0m4,300s
>> user	0m0,047s
>> sys	0m0,455s
```

## Conclusión

### Pruebas de exploración
| Prueba                       | Parámetros                | Bytes enviados | Bytes recibidos | Errores | Tiempo real (s) |
|------------------------------|---------------------------|----------------|-----------------|---------|-----------------|
| **Local (Imagen, size 1024)** | Timeout: 3, Input: in.jpeg | 67008          | 67008           | 0       | 3.056           |
| **Local (Imagen, size 1 byte)** | Timeout: 3, Input: in.jpeg | 267231         | 267231          | 0       | 14.018          |
| **Anakena (Imagen, size 1024)** | Timeout: 3, Input: in.jpeg | 67008          | 67008           | 0       | 3.547           |
| **Anakena (Imagen, size 256)**  | Timeout: 3, Input: in.jpeg | 67593          | 71996           | 10      | 5.198           |

### Archivo de 500MB y 500KB respectivamente
| Prueba                       | Parámetros                | Bytes enviados | Bytes recibidos | Errores | Tiempo real (s) |
|------------------------------|---------------------------|----------------|-----------------|---------|-----------------|
| **Local (500MB, size 1024)**  | Timeout: 3                | 525824003      | 525824003       | 0       | 106.397         |
| **Local (500MB, size 32768)** | Timeout: 0.001            | 524336003      | 585683315       | 1872    | 8.884           |
| **Anakena (500KB, size 1024)**| Timeout: 3                | 513503         | 522746          | 0       | 7.125           |
| **Anakena (500KB, size 8192)**| Timeout: 3                | 512192         | 512192          | 0       | 3.823           |
| **Anakena (500KB, size 1024)**| Timeout: 0.01             | 513503         | 728146          | 207     | 5.101           |
| **Anakena (500KB, size 8192)**| Timeout: 0.01             | 512753         | 1261368         | 365     | 4.300           |

1. Si el archivo de salida es más pequeño que el de entrada, ¿puede ocurrir aunque mi protocolo esté bien implementado?

No es correcto, pues si el protocolo Stop-and-Wait está bien implementado, el archivo de salida debe ser exactamente igual al de entrada, incluyendo el tamaño. Si el de salida es más chico puede ser que uno o más paquetes se perdieron sin ser retransmitidos correctamente, o que se terminó la recepción antes de tiempo. En mis pruebas, esto ocurrió solo cuando usé timeouts extremadamente bajos (como 0.001), lo que causó múltiples retransmisiones y eventualmente errores no recuperados, indicando que en ese caso el protocolo falló en su objetivo. Pero en estos casos el archivo de salida "acumuló" los paquetes recibidos y terminó con un tamaño superior al del input.

2. Los valores de ancho de banda medidos en esta tarea son muy distintos a los de la T1 y T2. ¿cuál es la causa principal de estas diferencias?

La causa principal es la naturaleza secuencial del protocolo Stop-and-Wait, que impone una espera activa entre cada envío y recepción de paquete.
En las tareas anteriores, no se implementó un formato que permitiera distinguir las emisiones y recepciones de los paquetes, sin esto, los paquetes podían fluir más rápidamente, a costa de errores o pérdida de datos.
Además en esta tarea se hace una doble confirmación de cada paquete, el cual debe ser confirmado antes de enviar el siguiente, y cualquier retransmisión implica repetir todo ese ciclo. Esto reduce drásticamente el rendimiento efectivo, especialmente si el timeout es mal calibrado o si la latencia es alta (como al usar Anakena). 

3. Dijimos que un protocolo bien implementado no debiera nunca morir por el timeout de 3 segundos puesto en el socket de recepción. ¿Por qué es esto así?

El timeout de 3 segundos es un "límite de seguridad" y no es una parte activa del protocolo, es decir, ese timeout solo se alcanzará cuando haya un error externo al protocolo en sí. Es utilizado como medida de precaución para evitar que el thread receptor quede bloqueado indefinidamente si no recibe datos o confirma el último paquete en el tiempo esperado. Sin embargo, en nuestro caso la confirmación de los paquetes se hace de manera muy rápida pues no se envía nada a través del socket, si no que se modifica una variable global. AL disminuir el timeout obtuvimos errores pero estos están relacionados a retrasos en el envío del paquete más que a su pérdida. De hecho no tuvimos ninguna pérdida de paquetes, más bien retrasos que conllevaron a un reenvío de ciertos paquetes y sus dobles recepciones en el archivo de salida.