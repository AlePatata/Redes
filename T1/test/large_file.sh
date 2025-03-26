#!/bin/bash

HOST_LOCAL="127.0.0.1"
HOST_ANAKENA="anakena.dcc.uchile.cl"
PORT="1818"
SIZES="1024 4096 8192" 
INPUT_FILE="put/big_in.dat" 
OUTPUT_FILE="put/big_out.dat"
RESULTS_FILE="test/results.txt"

echo "Generando archivo grande de 500MB..."
dd if=/dev/zero of="$INPUT_FILE" bs=500M count=1 status=none
run_test() {
    local host=$1
    local title=$2
    
    echo "===== $title =====" >> "$RESULTS_FILE"
    for size in $SIZES; do
        echo "Buffer size: $size bytes" >> "$RESULTS_FILE"
        
        # Capturar tiempo y salida separadamente
        exec 3>&1 
    time_output=$( { time python3 client_bw.py $size $HOST_LOCAL $PORT < $INPUT_FILE > $OUTPUT_FILE >&3; } 2>&1 )
        exec 3>&-  # Cerrar descriptor
        
        # Extraer y formatear tiempos
        real_time=$(echo "$time_output" | grep real | awk '{print $2}')
        user_time=$(echo "$time_output" | grep user | awk '{print $2}')
        sys_time=$(echo "$time_output" | grep sys | awk '{print $2}')
        
        printf "real\t%s\nuser\t%s\nsys\t%s\n" "$real_time" "$user_time" "$sys_time" >> "$RESULTS_FILE"
        echo "-------------------------" >> "$RESULTS_FILE"
    done
}

# Limpiar archivo de resultados
> "$RESULTS_FILE"

# Ejecutar pruebas
run_test "$HOST_LOCAL" "Pruebas en LOCALHOST"
echo -e "\n\n" >> "$RESULTS_FILE"
run_test "$HOST_ANAKENA" "Pruebas en ANAKENA"

echo "Pruebas completadas. Resultados en $RESULTS_FILE"