#!/bin/bash

HOST_LOCAL="127.0.0.1"
HOST_ANAKENA="anakena.dcc.uchile.cl"
PORT="1818"
SIZES="1024 4096 8192"
NUM_FILES=100
INPUT_DIR="put/smalls_in"
OUTPUT_DIR="put/smalls_out"
RESULTS_FILE="test/results.md"


mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"
> RESULTS_FILE

generate_files() {
    local num_files=$1
    echo "Generando $num_files archivos pequeños (5MB cada uno)..."
    for i in $(seq 1 $num_files); do
        dd if=/dev/zero of="$INPUT_DIR/file_$i.dat" bs=5M count=1 status=none
    done
}

run_client() {
    local input_file="$1"
    local output_file="${OUTPUT_DIR}/$(basename "$input_file")"
    ./client_bw.py "$SIZE" "$input_file" "$output_file" "$HOST" "$PORT";
}
export -f run_client

run_parallel_test() {
    local host=$1
    local title=$2

    echo "# $title" >> "$RESULTS_FILE"

    for size in $SIZES; do
        SIZE=$size
        HOST=$host

        echo "## Tamaño de buffer: $SIZE bytes" >> "$RESULTS_FILE"

        # Regenerar archivos
        rm -f "$INPUT_DIR"/* "$OUTPUT_DIR"/*
        generate_files "$NUM_FILES"

        start=$(date +%s.%N)
        export HOST PORT SIZE
        find "$INPUT_DIR" -type f -print0 | xargs -0 -P "$NUM_FILES" -I {} bash -c 'run_client "{}"' 

        end=$(date +%s.%N) >> "$RESULTS_FILE"

        elapsed=$(echo "$end - $start" | bc -l)
        printf "**Tiempo total (100 clientes)**: %.4f segundos\n" "$elapsed" >> "$RESULTS_FILE"
        echo "-------------------------" >> "$RESULTS_FILE"
    done
}

run_parallel_test "$HOST_LOCAL" "Pruebas paralelas en LOCALHOST"
run_parallel_test "$HOST_ANAKENA" "Pruebas paralelas en ANAKENA"

echo "Pruebas completadas. Resultados en $RESULTS_FILE"