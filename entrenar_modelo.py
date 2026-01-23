import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

print("Cargando dataset...")
df = pd.read_csv('dataset_servicios_inteligente.csv')
X = df.drop('score', axis=1)
y = df['score']

print(f"Entrenando modelo con {len(df)} registros...")

# Ajustamos para que el archivo pese poco: menos árboles y menos profundidad
rf = RandomForestRegressor(
    n_estimators=50,   # Menos árboles = archivo más pequeño
    max_depth=10,      # Menos profundidad = archivo más pequeño
    random_state=42,
    n_jobs=-1
)
rf.fit(X, y)

# Guardar con compresión para reducir aún más el tamaño
joblib.dump(rf, 'polimapa_brain_servicios.joblib', compress=3)
print("Cerebro guardado exitosamente (versión ligera).")