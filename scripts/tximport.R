# ===========================================================================
# =                            imports
# ===========================================================================

library(readr)
library(tximport)

# ===========================================================================
# =                            code
# ===========================================================================

# Nombramos archivo tx2gene con datos de tx y gene id
tx2gene <- read.delim("results/tx2gene_awk.tsv", sep = '\t')
colnames(tx2gene) <- c("Tx","Gene")

vector <- list.files("results/salmon_results",
                     pattern = "quant.sf",
                     full.names = TRUE,
                     recursive = TRUE)


samples <- basename(dirname(vector))
samples <- sub("_.*", "", samples)

# ==================================PARÁMETROS=========================================
# Parámetros: 
# vector con direcciones de archivos quant.sf a meter
# type: Pseudoalineador que creó los datos (salmon)
# tx2gene: Archivo de referencia con transcript idq() y gene id

tx_matrix <- tximport(vector, type="salmon", tx2gene=tx2gene, ignoreTxVersion = TRUE)

colnames(tx_matrix$counts) <- samples

# Crear la carpeta si no existe
dir.create("results/count_matrix", recursive = TRUE, showWarnings = FALSE)

# Guardamos matriz de conteos y objeto txi para usar en DESeq2
write.table(tx_matrix$counts, file = "results/count_matrix/tximport_counts.tsv")

saveRDS(tx_matrix, file = "results/count_matrix/txi_data.rds")