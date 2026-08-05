# Fases del procesamiento

## Ambiente de conda

Activar con el comando: conda activate molecular_clock

### Descarga de archivos fastq 
Se utilizó el código "Descarga_SRR.sh" con el programa fasterq-dump : 3.2.1 del ambiente de sra-tools para bajar los 143 archivos fastq del del proyecto  (https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA454681&o=acc_s%3Aa) con el archivo de metadata SraRunTable.csv guardado en la carpaeta "data" . Sin embargo, al finalizar el proceso sólo 116 muestras fueron descargadas correctamente.

### Análisis Fastqc
Se usó el código Fastqc_multiqc.sh con las versiones de FastQC 0.12.1 y multiqc version 1.28 para crear archivos para analizar la calidad de las lecturas. 

Las lecturas se ven lo suficientemente descentes para proceder. 

### Descarga de datos para índice de referencia de salmon
Se utilizó el archivo GTF de Gencode gencode.v49.annotation.gtf, así como el archivo fasta gencode.v49.transcripts.fa.gz 
y GRCh38.primary_assembly.genome.fa.gz para generar el índice de salmon y hacer los análisis posteriores.

Se depositaron los archivos en la carpeta data/Salmon_reference.

###  Indexar el genoma y transcriptoma para obtener las estimaciones de cuantificación adecuadas
Todo se corrió en la carpeta data/Salmon_reference con salmon 1.10.3

grep "^>" <(gunzip -c GRCh38.primary_assembly.genome.fa.gz) | cut -d " " -f 1 > decoys.txt
sed -i.bak -e 's/>//g' decoys.txt

cat gencode.v49.transcripts.fa.gz GRCh38.primary_assembly.genome.fa.gz > gentrome.fa.gz

salmon index -t gentrome.fa.gz -d decoys.txt -p 12 -i ../salmon_index --gencode

### Pseudoalineamientos con salmon 
Se corre el script Salmon.py 
(Hecho para lecturas no pareadas)

### Creación de archivo  tx2gene
Se crea archivo tx2gene_awk.tsv con el script tx2gene.awk proporcionándole el archivo gencode.v49.annotation.gtf y tomando los transcript id en columna 1 y gene id en columna 2 

Comando corrido en carpeta Molecular_clock: awk -f scripts/tx2gene.awk data/Salmon_reference/gencode.v49.annotation.gtf > results/tx2gene_awk.tsv

### Creación de matrices con tximport 
Se corre el código tximport.R creando la matriz raw de los pseudocounts de las muestras.
Se guarda la salida de counts y de objeto tximport en results/count_matrix.

Comando corrido en Molecular_clock: Rscript scripts/tximport.R
### Normalización de matriz
Se corre el código NormalizationDeseq2.R para normalizar las proporciones de secuencias y retirar transcritos poco expresados. 

Comando corrido en Molecular_clock: Rscript scripts/NormalizationDeseq2.R 

### Prueba de permutación 
Para la prueba de permutación, correr el script Permutation_test.py parado en la carpeta scripts.
Dejamos pasar transcritos con padj menor a .1 siendo laxos al ser un filtro inicial y por recuperar muy pocos transcritos antes con .05 y .01

### Matriz con niveles de expresiín en percentiles
Se corrió el script "percentil_filtered_genes.py" parado en la carpeta scripts y se guardó la matriz nueva en results/percentil_matrix.

ram.tsv y percentil.tsv cuentan con los mismos genes, pero percentil los números se encuentran al cuadrado y en percentiles y raw son los transcritos normalizados sin elevar al cuadrado.

### Análisis con Machine Learning
Para ello se hizo una mayor modificación del código y varios intentos con distintos parámetros. 


