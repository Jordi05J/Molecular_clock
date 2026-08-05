# Fases del procesamiento

## Cargar miniconda (en caso de no tenerlo)
Sigue las siguientes indicaciones para cambiar de ruta:
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda version 25.11.1

## Ambiente de conda
archivo environment.yml

Cómo correrlo: Estando parado dentro de la carpeta "Molecula_clock" correr "conda env create -f environment.yml"

De esta manera deben cargarse las librerías necesarias para correr los procesos. 

Para corres los programas de esta carpeta: "conda activate molecular_clock" 
Para dejar de usar: "conda deactivate"

### Descarga de archivos fastq 
Utilizar el código "Descarga_SRR.sh" en la carpeta "scripts" con el programa fasterq-dump : 3.2.1 del ambiente de sra-tools para bajar los archivos fastq de insterés.

En la carpeta Molecular_clock/data guardar el archivo csv "SraRunTable.csv" que puede ser obtenido en "https://www.ncbi.nlm.nih.gov/geo/" al introducir el id del Biproject, posteriormente seleccionando "Sra Run Selector" y descargando el archivo "Metadata"

OJO. El código asume que el archivo se encuentra en formato csv, que se llama "SraRunTable.csv" dentro de la carpeta "data", que tiene header y que los SRRs se encuentran en la primera columna, de no ser el caso debe ser modificado. 

Para hacer ejecutable el archivo, a la altura de Molecular_clock/scripts corre "chmod +x Descarga_SRR.sh". Posteriormente corre el archivo a esa altura con el comando "bash Descarga_SRR.sh"

### Análisis Fastqc
Usar el código "Fastqc_multiqc.sh" con las versiones de FastQC 0.12.1 y multiqc version 1.28 para crear archivos para analizar la calidad de las lecturas. 

Para hacer ejecutable el archivo, a la altura de Molecular_clock/scripts corre "chmod +x Fastqc_multiqc.sh". 
Para correr el script, ejecutar a la altura de Molecular_clock/scripts: bash Fastqc_multiqc.sh

Esto generará en results una carpeta fastqc y multiqc, de la cual en multiqc (recomendado) se puede descargar el archivo html para visualizar la calidad y determinar si es recomendable hacer limpieza o mantenerlo como está.

### Descarga de datos para índice de referencia de salmon
Buscar en Gencode https://www.gencodegenes.org/ (en caso de ser datos de humano o ratón) y descargar:
1. Archivo GTF de anotación.
2. Archivo FASTA.
3. Archivo primary_assembly.genome.

Estos deben ser guardados en una carpeta que nombrarás "Salmon_reference" dentro de "data".
Comando a la altura de carpeta Molecular_clock: "mkdir data/Salmon_reference".

###  Indexar tu genoma y transcriptoma para obtener los estimados de cuantificación adecuados (accurate quantification estimates).
(Remplazar los x con los nombres de tus archivos)
x1 = nombre de tu archivo primary_assembly.genome.fa.gz
x2 = nombre de archivo transcripts.fa.gz

Correr parado en la carpeta data/Salmon_reference

grep "^>" <(gunzip -c x1) | cut -d " " -f 1 > decoys.txt

sed -i.bak -e 's/>//g' decoys.txt

cat x2 x1 > gentrome.fa.gz

salmon index -t gentrome.fa.gz -d decoys.txt -p 12 -i ../salmon_index --gencode

Con esto se generará la carpeta con el índice de salmon 

### Pseudoalineamientos con salmon 
Se corre el script "Salmon.py" parado en la carpeta "scripts".

Se corre con el comando: python3 Salmon.py

OJO. Este código asume que las lecturas son no pareadas y que sólo hay un archivo fastq por carpeta, si no fuera el caso debe modificarse el código o borrar uel archivo fastq.2 en las carpetas. 

### Creación de archivo  tx2gene
Se crea archivo tx2gene_awk.tsv con el script "tx2gene.awk" proporcionándole el archivo annotation.gtf y tomando los transcript id en columna 1 y gene id en columna 2 

x3 = nombre de archivo annotation.gtf

Correr parado en la carpeta Molecular_clock: awk -f scripts/tx2gene.awk data/Salmon_reference/x3 > results/tx2gene_awk.tsv

### Creación de matrices con tximport 
Crea la carpeta corriendo en la carpeta Molecular_clock este comando (en caso de que el código no funcione por no poder crear la carpeta): "mkdir results/count_matrix"

Se corre el código "tximport.R" creando la matriz raw de los pseudocounts de las muestras.

Correr parado en la carpeta Molecular_clock: "Rscript scripts/tximport.R"

La salida del proceso (matriz con transcritos) se guarda en "Molecular_clock/results/count_matrix"

### Normalización de matriz
Crea la carpeta corriendo en la carpeta Molecular_clock este comando (en caso de que el código no funcione por no poder crear la carpeta): "mkdir results/normalized_matrix"

Se corre el código "NormalizationDeseq2.R" para normalizar las proporciones de secuencias y retirar transcritos poco expresados. 

Correr parado en la carpeta Molecular_clock: "Rscript scripts/NormalizationDeseq2.R"

La salida de matriz normalizada se guarda en "results/normalized_matrix/normalized_counts.tsv"

### Prueba de permutación 
Para la prueba de permutación, correr el script "Permutation_test.py" parado en la carpeta "scripts"

OJO. Dependiendo lo que busques hacer debes modificar los siguientes parámetros:
1. age_range. (tamaño de la vantana basado en la edad numérica que aparezca en el archivo SraRunTable.csv (si por alguna razón no fuera numérica debe modificarse esa cuestión en el código)).
2. permutations. (esto es más opcional, dependiendo de lo que consideren)
3. name. (nombre del archivo salida, puedes renombrarlo diferente si haces más de una prueba).
4. padj. (valor de pvalue ajustado que usarás para determianr diferencia significativa)

Correr a la altura de scripts: "python3 Permutation_test.py"
OJO. Puedes considerar correr "nohup python3 Permutation_test.py &" para que se corra en segundo plano si gustas. 

La salida se guarda en "/results/permutation_genes"

### Matriz con niveles de expresión en percentiles
Correr el script "percentil_filtered_genes.py" parado en la carpeta scripts. 

Salida del código en "results/percentil_matrix"




