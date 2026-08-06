# ======================================
#           IMPORTS
# ======================================
import pandas as pd
import numpy as np
import os
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt

# ======================================
#           FUNCTIONS
# ======================================

def column_age(data, SraTable):
    '''
    Agrega la columna de edad a el dataframe de expresión genética
    
    Args:
        data (pd.DataFrame): DataFrame con la expresión genética
        SraTable (pd.DataFrame): DataFrame con la información de las muestras, incluyendo edad
    
    Returns:
        pd.DataFrame: DataFrame con la columna de edad agregada
    '''
    ages = []
    for index, row in data.iterrows():
        for index2, row2 in SraTable.iterrows():
            if row2['Run'] == index:
                ages.append(row2['age'])
    data['age'] = ages
    return data

def split_data(data):
    '''
    Divide el dataset en conjuntos de entrenamiento y prueba.
    
    Args:
        data (pd.DataFrame): DataFrame con la expresión genética y la columna de edad.
    
    Returns:
        tuple: Conjuntos de entrenamiento y prueba (X_train, X_test, y_train, y_test).
    '''
    X = data.drop('age', axis=1)
    y = data['age']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    
    return X_train, X_test, y_train, y_test

def random_forest_model(X_train, y_train, X_test, y_test, images_dir):
    '''
    Entrena un modelo de regresión Random Forest.
    
    Args:
        X_train (pd.DataFrame): Conjunto de entrenamiento con las características.
        y_train (pd.Series): Conjunto de entrenamiento con las etiquetas (edad).
    
    Returns:
        RandomForestRegressor: Modelo entrenado de regresión Random Forest.
    '''
    os.makedirs(images_dir, exist_ok=True)
    r2_scores = []
    n_estimators = [50, 100, 200, 300, 500]
    models = {}
    for n in n_estimators:
        model = RandomForestRegressor(n_estimators=n, random_state=1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        models[n] = model
        r2_scores.append(r2_score(y_test, y_pred))
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.6)
        xmin = min(y_test.min(), y_pred.min())
        xmax = max(y_test.max(), y_pred.max())

        plt.plot([xmin, xmax], [xmin, xmax], 'r--')

        plt.xlabel("True Age")
        plt.ylabel("Predicted Age")
        plt.title(f"Random Forest ({n} trees)")
        plt.savefig(f'{images_dir}/prediction_error_n_{n}.png')
    return n_estimators, r2_scores, models

# ======================================
#           MAIN
# ======================================

if __name__ == "__main__":
    # Caragmos dataset y tabla de metadatos (cambia el nombre para analizar raw.tsv/percentil.tsv)
    data = pd.read_csv('../results/percentil_matrix/raw.tsv', sep='\t', header=0, index_col=0)
    data = data.T
    SraTable = pd.read_csv('../data/SraRunTable.csv')
    
    # Agregamos edad a nuestro dataset
    data_age = column_age(data,SraTable)
    data_age["age"] = pd.to_numeric(data_age["age"], errors="coerce")

    n_removed = data_age["age"].isna().sum()
    print(f"Se eliminaron {n_removed} muestras con edades no numéricas.")

    data_age = data_age.dropna(subset=["age"])
    print(data_age["age"].dtype)

    # Dividimos el dataset en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = split_data(data_age)
    
    # Cambia el nombre del directorio para las imágenes (percentil_matrix o raw_matrix por ejemplo)
    images_dir = '../results/images/raw_matrix'
    # Entrenamos el modelo de regresión Random Forest
    n_estimators, r2_scores, models = random_forest_model(X_train, y_train, X_test, y_test, images_dir)
    
    # Graficamos la mandamos a results
    
    plt.figure(figsize=(10, 6))
    plt.plot(n_estimators, r2_scores, marker='o')
    plt.title('R2 Score vs Number of Estimators')
    plt.xlabel('Number of Estimators')
    plt.ylabel('R2 Score')
    plt.xticks(n_estimators)
    plt.grid()
    plt.savefig(f'{images_dir}/r2_score.png')
    