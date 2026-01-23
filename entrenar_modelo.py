import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

df = pd.read_csv('dataset_servicios_inteligente.csv')
X = df.drop('score', axis=1)
y = df['score']

print(f"Entrenando con columnas: {list(X.columns)}")
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X, y)

joblib.dump(rf, 'polimapa_brain_servicios.joblib')
print("Modelo guardado como polimapa_brain_servicios.joblib")