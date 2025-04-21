#!/bin/bash

HOST_LOCAL="127.0.0.1"
HOST_ANAKENA="anakena.dcc.uchile.cl"
PORT="1818"
SIZES="1024 4096 8192" 
INPUT_FILE="put/big_in.dat" 
OUTPUT_FILE="put/big_out.dat"
RESULTS_FILE="test/results.txt"

# Crear directorios necesarios
mkdir -p put test

echo "Generando archivo grande de 500MB..."
dd if=/dev/zero of="$INPUT_FILE" bs=500M count=1 status=none

run_test() {
    local host=$1
    local title=$2
    
    echo "===== $title =====" >> "$RESULTS_FILE"
    for size in $SIZES; do
        echo "Buffer size: $size bytes" >> "$RESULTS_FILE"
        
        # Medir tiempo de forma más confiable
        start_time=$(date +%s.%N)
        python3 client_bw.py $size $INPUT_FILE $OUTPUT_FILE $host $PORT
        exit_code=$?
        end_time=$(date +%s.%N)
        
        elapsed_time=$(LC_NUMERIC=C bc <<< "$end_time - $start_time")
        
        if [ $exit_code -ne 0 ]; then
            echo "ERROR: El cliente falló con código $exit_code" >> "$RESULTS_FILE"
        else
            printf "real\t%.4f s\n" $elapsed_time >> "$RESULTS_FILE"
            
            # Verificar integridad del archivo
            if cmp -s "$INPUT_FILE" "$OUTPUT_FILE"; then
                echo "status\tArchivos coinciden" >> "$RESULTS_FILE"
            else
                echo "status\tERROR: Archivos difieren" >> "$RESULTS_FILE"
            fi
        fi
        
        echo "-------------------------" >> "$RESULTS_FILE"
    done
}

# Limpiar archivo de resultados
> "$RESULTS_FILE"

# Ejecutar solo pruebas locales
run_test "$HOST_LOCAL" "Pruebas en LOCALHOST"

# Ejecutar solo pruebas locales
run_test "$HOST_ANAKENA" "Pruebas en ANAKENA"


echo "Pruebas completadas. Resultados en $RESULTS_FILE"