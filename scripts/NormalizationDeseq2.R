# ===========================================================================
# =                            imports
# ===========================================================================

library(DESeq2)

# ===========================================================================
# =                            code
# ===========================================================================
txi <- readRDS("results/count_matrix/txi_data.rds")

# Nombres de las muestras
sampleTable <- data.frame(row.names = colnames(txi$counts))

# Crear objeto DESeqDataSet
dds <- DESeqDataSetFromTximport(txi, colData=sampleTable, design= ~ 1)

# Estimar los factores de tamaño (necesario para calcular CPM/FPM correctamente)
dds <- estimateSizeFactors(dds)

# Calcular los Counts Per Million (CPM)
cpm_matrix <- fpm(dds, robust = FALSE)

# Dejar genes donde el CPM sea >= 1 en al menos 10 muestras
keep <- rowSums(cpm_matrix >= 1) >= 10

# Filtrar el objeto DESeqDataSet original
dds_filtered <- dds[keep, ]

# Extraer la matriz de conteos normalizados (y filtrados)
conteos_normalizados <- counts(dds_filtered, normalized = TRUE)

# Crear la carpeta si no existe
dir.create("results/normalized_matrix", recursive = TRUE, showWarnings = FALSE)

# Guardar como archivo tsv para usar en análisis posteriores
write.table(conteos_normalizados, file = "results/normalized_matrix/normalized_counts.tsv", sep = "\t")