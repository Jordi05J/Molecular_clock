# 1. Import necessary modules
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score

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

# Caragmos dataset y tabla de metadatos
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



# 3. Scale features (Highly recommended for SVMs)
sc_X = StandardScaler()
sc_y = StandardScaler()

X_train_scaled = sc_X.fit_transform(X_train)
X_test_scaled = sc_X.transform(X_test)

# For y, SVR performs best when targets are also scaled
y_train_scaled = sc_y.fit_transform(y_train.values.reshape(-1, 1)).ravel()

# 4. Initialize and train the SVR model
# (Kernels can be 'linear', 'poly', or 'rbf' depending on your data)
regressor = SVR(kernel='rbf', C=1.0, epsilon=0.1)
regressor.fit(X_train_scaled, y_train_scaled)

# 5. Make predictions
X_test_scaled = sc_X.transform(X_test) # Scale test data
y_pred_scaled = regressor.predict(X_test_scaled)

# Reverse the scaling to get predictions back to original values
y_pred = sc_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

# 6. Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")