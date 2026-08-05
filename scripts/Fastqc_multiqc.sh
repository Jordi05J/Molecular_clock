#!/bin/bash

# Rutas de directorios a tomar datos y crear
FASTQ_DIR="../data/SRRs"
FASTQC_DIR="../results/fastqc"
MULTIQC_DIR="../results/multiqc"

# Crear directorios de salida si no existen
mkdir -p "$FASTQC_DIR"
mkdir -p "$MULTIQC_DIR" 

# Correr FastQC para cada archivo FASTQ
for SRR_DIR in "$FASTQ_DIR"/*; do
    if [ -d "$SRR_DIR" ]; then
        SRR=$(basename "$SRR_DIR")
        echo "Procesando $SRR"
        nohup fastqc -o "$FASTQC_DIR" "$SRR_DIR"/*.fastq &
    fi
done

wait # Esperar a que todos los procesos de FastQC terminen

# Correr MultiQC para compilar los resultados de FastQC
nohup multiqc -o "$MULTIQC_DIR" "$FASTQC_DIR" &