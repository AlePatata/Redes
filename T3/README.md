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
En este caso no se obtuvo ningun error y la diferencia de bytes enviados con respecto al tamaño de la imagen corresponde a la cantidad de paquetes enviados (67 contando uno vacío) por los bytes añadidos en cada prefijo de 3 digitos.
### Anakena
En anakena se obtuvo un resultado muy similar, donde finalmente se imprimió en la terminal un resultado:
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

