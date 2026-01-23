import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

print("Cargando dataset...")
try:
    df = pd.read_csv('dataset_servicios_inteligente.csv')
except FileNotFoundError:
    print("Error: Ejecuta primero 'generar_datos.py'")
    exit()

# Features (X) y Target (y)
X = df.drop('score', axis=1)
y = df['score']

print(f"Entrenando modelo con {len(df)} registros y {X.shape[1]} variables...")

# Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
rf.fit(X, y)

archivo = 'polimapa_brain_servicios.joblib'
joblib.dump(rf, archivo)
print(f"Cerebro guardado en: {archivo}")