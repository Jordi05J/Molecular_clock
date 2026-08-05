#!/bin/bash

# Ruta al archivo con los SRRs
SRR_LIST="../data/SraRunTable.csv"

# Directorio donde se guardarán los archivos
OUTPUT_DIR="../data/SRRs"

# Crear el directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

# Leer cada SRR desde el archivo
# Procesa la primera columna del CSV, asumiendo que el formato es "SRR,otros_datos" y omitiendo la primera línea (cabecera)
tail -n +2 "$SRR_LIST" | while IFS=',' read -r SRR _; do
    echo "Procesando $SRR"
    # Crear una carpeta para cada SRR
    mkdir -p "$OUTPUT_DIR/$SRR"

    # Descargar el archivo con fasterq-dump 
    nohup fasterq-dump --threads 6 --progress --split-3 -O "$OUTPUT_DIR/$SRR" "$SRR" > "$OUTPUT_DIR/$SRR/fastq2-dump.log" 2>&1 &

    # Pausa para no sobrecargar el equipo
    sleep 1
done < "$SRR_LIST"
