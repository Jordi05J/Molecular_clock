# ===========================================================================
# =                            imports
# ===========================================================================

import os 
import subprocess

# ===========================================================================
# =                            functions
# ===========================================================================

def run_salmon_unpaired(salmon_index, SRRs_path, salmon_output):

    '''
    Programa para correr el programa salmon con lecturas no pareadas (single/unpaired) de archivos SRR  

    Returns: Directorios de corridas no pareadas con información de las corridas
    '''

    os.makedirs(salmon_output, exist_ok=True)
    # Recorremos la estructura de directorios y sacamos cada archivo fastq
    for sample in os.listdir(SRRs_path):
        sample_path = os.path.join(SRRs_path, sample)
        for file in os.listdir(sample_path):
            if file .endswith(".fastq"):
                file_path = os.path.join(sample_path, file)
                # Nombre del archivo de salida sin .fastq
                file_name = os.path.splitext(file)[0]
            
                # Definimos el nombre de los archivos de salida
                SRR_output_dir = os.path.join(salmon_output, file_name ,f"{file_name}_unpaired_salmon")
                os.makedirs(SRR_output_dir, exist_ok=True)
                
                """
                Parámetros:
                -i: archivo index de salmon
                -l: librería usada (strandedness "A") infiere el tipo de librería automáticamente
                -r: archivo fastq
                -o: Nombre y ruta de directorio salida.
                """

                # Comando a correr con index, ruta del archivo fastq y nombre del archivo de salida
                salmon_unpaired_cmd = f"salmon quant -i {salmon_index} -l A -r {file_path} -o {SRR_output_dir}"
                subprocess.run(salmon_unpaired_cmd, shell=True, check=True)

    print("Finalizó el proceso de salmon con lecturas no pareadas (single/unpaired)")


# ===========================================================================
# =                            main 
# ===========================================================================
if __name__ == "__main__":
    
    # Ruta de índice de salmon
    salmon_index = "data/salmon_index"

    # Ruta donde se encuentran los archivos a correr
    SRRs_path = "data/SRRs"

    # Ruta donde se guardaran los alineamientos
    salmon_output = "results/salmon_results"

    run_salmon_unpaired(salmon_index, SRRs_path, salmon_output)
    