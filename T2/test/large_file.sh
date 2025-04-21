#!/bin/bash

HOST_LOCAL="127.0.0.1"
HOST_ANAKENA="anakena.dcc.uchile.cl"
PORT="1818"
SIZES="1024 4096 8192" 
INPUT_FILE="put/big_in.dat" 
OUTPUT_FILE="put/big_out.dat"
RESULTS_FILE="test/results.md"

# Crear directorios necesarios
mkdir -p put test

echo "Generando archivo grande de 500MB..."
dd if=/dev/zero of="$INPUT_FILE" bs=500M count=1 status=none

run_test() {
    local host=$1
    local title=$2
    
    echo "# $title " >> "$RESULTS_FILE"
    for size in $SIZES; do
        echo "Size of buffer: $size bytes" >> "$RESULTS_FILE"
        start=$(date +%s.%N)
        ./client_bw.py $size $INPUT_FILE $OUTPUT_FILE $host $PORT;
        exit_code=$?
        end=$(date +%s.%N)
        elapsed=$(LC_NUMERIC=C bc <<< "$end - $start")
        
        if [ $exit_code -ne 0 ]; then
            echo "## ERROR: $exit_code" >> "$RESULTS_FILE"
        else
            printf "**time**: %s\n" "$elapsed" >> "$RESULTS_FILE"

        fi
        
        echo "-------------------------" >> "$RESULTS_FILE"
    done
}

> "$RESULTS_FILE"

run_test "$HOST_LOCAL" "Pruebas en LOCALHOST"

run_test "$HOST_ANAKENA" "Pruebas en ANAKENA"


echo "Pruebas completadas. Resultados en $RESULTS_FILE"