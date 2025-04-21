#!/bin/bash

HOST="127.0.0.1"
PORT="1818"
SIZE="1024"
INPUT_DIR="put/smalls_in" 
OUTPUT_DIR="put/smalls_out"
NUM_FILES=100
RESULTS_FILE="test/small_results_1024.txt"

# Crear directorios si no existen
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"
# Limpieza de resultados
> RESULTS_FILE

echo "Generando $NUM_FILES archivos pequeños (5MB cada uno)..."
for i in $(seq 1 $NUM_FILES); do
    dd if=/dev/zero of="$INPUT_DIR/file_$i.dat" bs=5M count=1
    dd if=/dev/zero of="$OUTPUT_DIR/file_$i.dat" count=1
done

# Función que ejecuta el cliente para un archivo
run_client() {
    local input_file="$1"
    local output_file="${OUTPUT_DIR}/$(basename "$input_file")"
    echo "Ejecutando cliente para: $input_file"
    { time -p ./client_bw.py "$SIZE" "$input_file" "$output_file" "$HOST" "$PORT"; } 2>&1
}
export -f run_client

echo "Iniciando transferencia paralela de $NUM_FILES archivos..."

# Ejecución en paralelo con xargs
find "$INPUT_DIR" -type f -print0 | xargs -0 -P "$NUM_FILES" -I {} bash -c '
    file="{}"
    output=$(run_client "$file")
    echo "$output" | awk -v f="$file" '\''/real/ {r=$2} /user/ {u=$2} /sys/ {s=$2} END {printf "%s: %.4f real %.4f user %.4f sys\n", f, r, u, s}'\'' 
' >> "$RESULTS_FILE"

# Cálculo de tiempos promedios
echo -e "\n===== Resumen de tiempos para size 1024 MB =====" >> "$RESULTS_FILE"
grep "real" "$RESULTS_FILE" | awk '{real+=$3; user+=$5; sys+=$7} END {printf "Promedio: %.4f real %.4f user %.4f sys\n", real/NR, user/NR, sys/NR}' >> "$RESULTS_FILE"

echo "Prueba completada. Resultados en $RESULTS_FILE"
