# Tarea 1 REDES
## Cliente
Lo importante de esta tarea (el cliente) se llamó `client_bw.py` siguiendo el ejemplo del enunciado, que recibe un size, un host y un port, además de darle un archivo de entrada y otro de salida. Este cliente se hizo a partir de `client_echo3.py` solo que se quitaron los encodes y decodes, además de reemplazar las entradas y salidas estandar (prints) por el buffer de aquellos. Le quité el tiempo de espera de 3 segundos al final.

## Tests
Las pruebas se automatizaron (con ayuda de deepseek) en los archivos .sh de la carpeta test. Para correrlos de nuevo solo se debe asegurar de que tienes los permisos (`chmod +x test/<archivo>.sh`) y ejecutarlos con `./test/<archivo>.sh`.

Los test son:
- `large_file.sh`: Crea un archivo binario .dat de 500MB en la carpeta put/ y prueba enviarlo por el localhost y por anakena con tamaños de lectura/escritura de 1024, 4096 y 8192. Tarda como 10 minutos y deja los resultados en `test/results.txt`
- `small_files_1024.sh`: Crea 100 archivos binarios de 5MB cada uno en la carpeta put/smalls_in/ y una función a la que pueden acceder 100 threads paralelamente con -xargs. Deja los resultados en `test/smalls_results_1024.txt`. Envia los archivos con un tamaño lectura/escritura de 1024 y los deja en put/smalls_out/
- `small_files_4096.sh`: Hace lo mismo que el test anterior pero con tamaño de lectura/escritura de 4096. Deja los resultados en `test/smalls_results_4096.txt`