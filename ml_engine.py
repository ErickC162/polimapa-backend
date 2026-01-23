import joblib
import pandas as pd
import os

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None
        # Columnas exactas del entrenamiento
        self.cols = ['u_comida', 'u_estudio', 'u_hobby', 'match_comida', 'match_estudio', 'match_hobby', 'match_afinidad', 'popularidad']

    def recomendar_servicios(self, u_c, u_e, u_h, servicios_db):
        res = []
        for s in servicios_db:
            score = self._predecir(u_c, u_e, u_h, s)
            # El motivo se genera basándose en las preferencias
            motivo = "Lugar popular en el campus"
            if u_c in s.lista_comida: motivo = "Excelente para tu almuerzo"
            elif u_e in s.lista_estudio: motivo = "Ideal para estudiar"
            elif u_h in s.lista_hobby: motivo = "Perfecto para tu hobby"
            
            res.append({"servicio": s, "score": score, "motivo": motivo})
        
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:10]

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return float(s.popularidad)
        
        afinidad = {1:[2,3], 2:[1,3], 3:[1,2], 6:[3,4]}
        maf = 1 if uh in afinidad and set(s.lista_hobby).intersection(afinidad[uh]) else 0
        
        features = [
            uc, ue, uh,
            1 if uc in s.lista_comida else 0,
            1 if ue in s.lista_estudio else 0,
            1 if uh in s.lista_hobby else 0,
            maf,
            s.popularidad
        ]
        
        df_input = pd.DataFrame([features], columns=self.cols)
        return float(self.modelo.predict(df_input)[0])