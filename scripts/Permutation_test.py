# =====================================
#           IMPORTS
# =====================================

import os
import numpy as np
import pandas as pd
from datetime import datetime
import rpy2.robjects as ro
from statsmodels.stats.multitest import multipletests
from rpy2.robjects import pandas2ri

pandas2ri.activate()

# =====================================
#           FUNCTIONS
# =====================================

ro.r("""
library(coin)
library(BiocParallel)

options(digits = 22)

perm_test_all_genes <- function(expr_matrix, groups, permutations, cores=10) {

    expr_matrix <- as.matrix(expr_matrix)

    param <- SnowParam(workers = cores)

    pvals <- bplapply(seq_len(nrow(expr_matrix)), function(i) {

        gene_expr <- expr_matrix[i,]

        valid <- !is.na(gene_expr)
        gene_expr <- gene_expr[valid]
        grp <- groups[valid]

        if(length(unique(gene_expr[grp=="G1"])) < 2 || 
           length(unique(gene_expr[grp=="G2"])) < 2) {
            return(NA)
        }

        df <- data.frame(
            expression = gene_expr,
            group = factor(grp)
        )

        # Realizar el test
        test_result <- wilcox_test(
            expression ~ group,
            data = df,
            distribution = approximate(B = permutations)
        )
        
        W_obs <- statistic(test_result)
    
        # Extraer los estadísticos de las permutaciones generadas internamente
        # Nota: coin::wilcox_test no devuelve los W de permutaciones directamente,
        # así que la corrección clásica se hace sumando 1 a B
        p_val <- pvalue(test_result)[1]
        
        # Evitar p = 0 usando corrección mínima
        if(p_val == 0) {
        p_val <- 1 / (permutations + 1)
        }
        
        return(as.double(p_val))

    }, BPPARAM = param)

    return(unlist(pvals))
}
""")

def square_matrix(rute_to_matrix):
    '''
    Eleva al cuadrado las reads normaiizadas de la matriz de conteos 
    
    Args:
        rute_to_matrix (str): Ruta al archivo de la matriz de distancias con formato largo (long format).
    
    Returns:
        pd.DataFrame: Matriz de distancias en formato cuadrado (square format).
    '''
    matrix = pd.read_csv(rute_to_matrix, sep="\t", index_col=0)
    matrix2 = matrix ** 2
    return matrix2

def dic_SRR_age(rute_metadata, rute_SRRs):
    '''
    Crea un diccionario con los SRRs y sus respectivas edades.
    
    Args:
        rute_metadata (str): Ruta al archivo de metadatos (SraRunTable.csv).
        rute_SRRs (str): Ruta al directorio con los nombres de directorios de los SRRs.
    
    Returns:
        dict: Diccionario con los SRRs como claves y las edades como valores.
    '''
    # Crea un diccionario vacío para almacenar los SRRs y sus edades
    dic_SRR_age = {}

    # Leer el archivo de metadatos
    metadata = pd.read_csv(rute_metadata)
    
    # Leer el archivo de SRRs
    for dir in os.listdir(rute_SRRs):
        edad = metadata.loc[metadata['Run'] == dir, 'age'].values[0]
        dic_SRR_age[dir] = edad
    return dic_SRR_age

def permutation_test(matrix, dic_SRR_age, window, num_permutations, doc, pvadj, fdr=True):
    '''
    Analiza los niveles de expresión de cada uno de los genes comparando en ventanas.
    Si por ejemplo son de de edad de 10 años las ventanas son:
    1-5 años contra 6_10 años, luego 2_6 contra 7_11 años, etc.
    con un test de permutación y guarda aquellos que muestren una diferencia significativa (padj < filtro puesto) en un archivo de texto
    
    Args:
        matrix (pd.DataFrame): Matriz de distancias en formato cuadrado (square format).
        dic_SRR_age (dict): Diccionario con los SRRs como claves y las edades como valores.
        num_permutations (int, optional): Número de permutaciones a realizar. Por defecto es 1000.
        
    Returns:
        None: Guarda los resultados en un archivo de texto.
    '''
    
    # quedarse solo con edades numéricas
    edades = {k: int(v) for k, v in dic_SRR_age.items() if str(v).isdigit()}
    
    # Tomamos la edad mínima y máxima para definir las ventanas
    min_age = min(edades.values())
    max_age = max(edades.values())
    
    # Definimos la mitad para crear ambos grupos
    half = window // 2

    resultados = []
    for i in range(min_age, max_age - window + 2):
        print(f"Analizando ventana de edad: {i} a {i + window - 1} años. {datetime.now()}")
        # Valor medio y máximo de edad de la ventana 
        mid = i + half - 1
        end = i + window - 1

        # Se definen los grupos según la ventana de edad
        grupo1 = [k for k, v in edades.items() if i <= v <= mid]
        grupo2 = [k for k, v in edades.items() if mid < v <= end]
        
        
        if len(grupo1) < 2 or len(grupo2) < 2:
            continue  # saltar genes con datos insuficientes
        
        columnas = grupo1 + grupo2

        # Creamos submatriz de los SRRs que pertenecen a los grupos definidos
        submatrix = matrix[columnas]

        groups = ["G1"] * len(grupo1) + ["G2"] * len(grupo2)

        # Convertimos datos a R
        r_matrix = pandas2ri.py2rpy(submatrix)
        r_groups = ro.StrVector(groups)

        # Llamada a la función R
        pvals = ro.r["perm_test_all_genes"](
            r_matrix,
            r_groups,
            num_permutations
        )

        pvals = np.array(pvals, dtype=np.float64)

        for gene, pval in zip(submatrix.index, pvals):
            if np.isnan(pval):
                continue  # ignorar genes que no se pudieron testear
            
            resultados.append({
                "gene": gene,
                "window_start": i,
                "window_end": end,
                "pvalue": pval
            })

    # convertir a DataFrame
    resultados = pd.DataFrame(resultados)

    if resultados.empty:
        print("No hay resultados significativos.")
        return

    # aplicar corrección FDR
    if fdr:
        resultados["padj"] = multipletests(resultados["pvalue"], method="fdr_bh")[1]
        resultados = resultados[resultados["padj"] < pvadj]
        
    print(f"pvalue menor: {np.min(resultados['pvalue'])}")
    print(f"padj menor: {np.min(resultados['padj'])}")

    # guardar a TSV
    resultados.to_csv(
        f"../results/permutation_genes/{doc}",
        sep="\t",
        index=False,
        float_format="%.15e"
    )

    print(f"{len(resultados)} genes significativos guardados en '/results/permutation_genes/{doc}' {datetime.now()}")

# ======================================
#           MAIN
# ======================================

if __name__ == "__main__":

# Creamos matriz al cuadrado para el test de permutación
    print("Creando matriz al cuadrado... ", datetime.now())

    rute_to_matrix = "../results/normalized_matrix/normalized_counts.tsv"
    matrix2 = square_matrix(rute_to_matrix)
    
    print("Creando diccionario de SRRs y edades... ", datetime.now())
    # Creamos diccionario con los SRRs y sus edades
    rute_metadata = "../data/SraRunTable.csv"
    rute_SRRs = "../data/SRRs"
    dic_SRR_age = dic_SRR_age(rute_metadata, rute_SRRs)

    print("Realizando test de permutación... ", datetime.now())
    age_range = 10
    permutations = 10000
    name = "10000_significant_genes_1padj_2026_04_17.tsv"
    pvadj = 0.1
    permutation_test(matrix2, dic_SRR_age, age_range, permutations, name, pvadj)
