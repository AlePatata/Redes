#!/bin/bash

HOST_LOCAL="localhost"
HOST_ANAKENA="anakena.dcc.uchile.cl"
PORT="1818"
SIZES="1024 4096 8192" 
INPUT_FILE="put/archivo-grande.mkv"  # Archivo de entrada grande (ej. 500MB)
OUTPUT_FILE="put/output-grande.mkv"
RESULTS_FILE="test/results.txt"

# Pruebas en localhost
echo "===== Pruebas en LOCALHOST =====" > RESULTS_FILE
for size in $SIZES; do
    echo "Buffer size: $size bytes" >> RESULTS_FILE
    { time python3 client_bw.py $size $HOST_LOCAL $PORT < $INPUT_FILE > $OUTPUT_FILE ; } 2>> RESULTS_FILE
    echo "-------------------------" >> RESULTS_FILE
done

# Pruebas en anakena
echo "===== Pruebas en ANAKENA =====" >> RESULTS_FILE
for size in $SIZES; do
    echo "Buffer size: $size bytes" >> RESULTS_FILE
    { time python3 client_bw.py $size $HOST_ANAKENA $PORT < $INPUT_FILE > $OUTPUT_FILE ; } 2>> RESULTS_FILE
    echo "-------------------------" >> RESULTS_FILE
done

echo "Pruebas completadas. Resultados en $RESULTS_FILE"