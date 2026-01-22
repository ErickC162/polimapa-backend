import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

# 1. Cargar el dataset nuevo
print("Cargando dataset completo...")
try:
    df = pd.read_csv('dataset_servicios_epn_completo.csv')
except FileNotFoundError:
    print("Error: Ejecuta primero 'generar_datos.py'")
    exit()

# 2. Separar Features (X) y Target (y)
X = df.drop('match_score', axis=1)
y = df['match_score']

# 3. Entrenar Random Forest
print("Entrenando IA con todos los servicios...")
# Más profundidad (max_depth=15) para que aprenda bien las diferencias sutiles
modelo = RandomForestRegressor(n_estimators=150, random_state=42, max_depth=15)
modelo.fit(X, y)

# 4. Guardar cerebro
archivo = 'polimapa_brain_servicios.joblib'
joblib.dump(modelo, archivo)
print(f"Cerebro guardado en: {archivo}")