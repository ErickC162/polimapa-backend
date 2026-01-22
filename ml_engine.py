import joblib
import pandas as pd
import os
import random

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        try:
            self.modelo = joblib.load(ruta)
            print("✅ Motor ML cargado (Modo Servicios Completo).")
        except:
            print("⚠️ No se encontró modelo. Usando random.")
            self.modelo = None

    def predecir(self, usuario, servicio_db):
        if not self.modelo:
            return 0

        # Vector Usuario
        u_inputs = [
            usuario.pref_comida or 0, 
            usuario.pref_estudio or 0, 
            usuario.pref_hobby or 0
        ]
        
        # Vector Servicio (Desde BD)
        # Convierte booleanos a enteros
        s_inputs = [
            1 if servicio_db.es_lugar_comida else 0,
            1 if servicio_db.es_lugar_estudio else 0,
            1 if servicio_db.es_lugar_hobby else 0
        ]
        
        # Predicción
        cols = ['u_comida','u_estudio','u_hobby','s_comida','s_estudio','s_hobby']
        df = pd.DataFrame([u_inputs + s_inputs], columns=cols)
        
        return float(self.modelo.predict(df)[0])