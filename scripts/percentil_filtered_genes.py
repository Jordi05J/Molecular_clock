# =====================================
#           IMPORTS
# =====================================

import pandas as pd

# =====================================
#           FUNCTIONS
# =====================================

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

def filter_genes(df_norm_matrix, df_perm_genes):
    '''
    Filtra la matriz de expresión normalizada para conservar solo los genes que resultaron significativos en el test de permutación.
    
    Args:
        df_norm_matrix (pd.DataFrame): Dataframe de expresión normalizada.
        df_perm_genes (pd.DataFrame): Dataframe con los genes significativos del test de permutación.
    
    Returns:
        df_norm_matrix_filtered (pd.DataFrame): Dataframe filtrado con solo los genes significativos.
    '''
    uniq_genes = df_perm_genes.index.unique().tolist()

    df_norm_matrix_filtered = df_norm_matrix[df_norm_matrix.index.isin(uniq_genes)]
    
    return df_norm_matrix_filtered

def percentil_matrix(df_filtered):
    '''
    Calcular valores de percentil 1-100 para cada gen por individuo, con base en la matriz filtrada de genes significativos.
    Args:
        df_filtered (pd.DataFrame): Dataframe filtrado con solo los genes significativos.
    
    Returns:
        df_per (pd.DataFrame): Dataframe con los valores de percentil 1-100 para cada gen.
    '''
    df = pd.DataFrame()
    
    for column in df_filtered.columns:
        df_temp = pd.DataFrame()
        df_temp[column] = df_filtered[column].rank(pct=True) * 100
        df_temp[column] = df_temp[column].astype(int)
        df = pd.concat([df, df_temp], axis=1)
    df_per = pd.DataFrame(df.values, index=df_filtered.index, columns=df.columns)
    return df_per
    
# =====================================
#           MAIN
# =====================================

if __name__ == "__main__":

    # Dataframe de la matriz de expresión normalizada
    df_norm_matrix = pd.read_csv('../results/normalized_matrix/normalized_counts.tsv', sep = '\t',
                                header=0, index_col=0)
    # Dataframe de los genes significativos del test de permutación
    df_perm_genes = pd.read_csv('../results/permutation_genes/10000_significant_genes_1padj_2026_04_17.tsv',
                                sep = '\t', header=0, index_col=0)
   
    df_filtered = filter_genes(df_norm_matrix, df_perm_genes)
    # Matriz con cantidad de transcritos significativos con valores normalizados
    df_filtered.to_csv("../results/percentil_matrix/raw.tsv", sep = '\t')


    df_square_norm_matrix = square_matrix(df_filtered)
    df_percentil = percentil_matrix(df_square_norm_matrix)
    
    df_percentil.to_csv("../results/percentil_matrix/percentil.tsv", sep = '\t')
