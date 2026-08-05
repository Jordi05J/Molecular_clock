# Programa para crear archivo tx2gene con datos de referencia de gencode  
#
# Returns: imprime transcript id y gene id en formato tabular
# que pueden pasarse a un archivo

awk
BEGIN { FS = "\t" }

# Procesamos sólo las líneas donde de la tercera columna
$3 == "transcript" {
  split($9, attributes, "; ") # Se divide la columna 9 por ";"

  # Inicializamos las variables para almacenar los IDs de la transcripción y del gen.
  transcript_id = ""  
  gene_id = ""        

  # Itera sobre cada atributo en el arreglo 'attributes'.
  for (i in attributes) {
    split(attributes[i], key_value, " ") # Se dividen los atributos

    # Si la clave es "transcript_id", extraemos el valor correspondiente.
    if (key_value[1] == "transcript_id") {
      gsub(/"/, "", key_value[2]) # Elimina las comillas del valor.
      transcript_id = key_value[2] # Asigna el ID del transcrito 
      sub("\\..*", "", transcript_id) # Elimina cualquier parte después de un punto (.) en el ID.
    }
    # Si la clave es "gene_id", extraemos el valor correspondiente.
    else if (key_value[1] == "gene_id") {
      gsub(/"/, "", key_value[2]) # Elimina las comillas del valor.
      gene_id = key_value[2] # Asigna el ID del gen.
    }
  }

  # Si están ambos valores, se imprime
  if (transcript_id != "" && gene_id != "") {
    print transcript_id "\t" gene_id
  }
}