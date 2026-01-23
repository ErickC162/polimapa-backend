import joblib
import pandas as pd
import os

AFINIDAD_HOBBY = {1: [2, 3], 2: [1, 3], 3: [1, 2], 6: [3, 4]}

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None

    def recomendar_servicios(self, u_comida, u_estudio, u_hobby, servicios_db):
        resultados = []
        for s in servicios_db:
            score = self._predecir_score(u_comida, u_estudio, u_hobby, s)
            
            # Motivo simple basado en match
            motivo = "Lugar popular en el campus"
            if u_comida in s.lista_comida: motivo = "Coincide con tu gusto de comida"
            elif u_estudio in s.lista_estudio: motivo = "Ideal para estudiar"
            elif u_hobby in s.lista_hobby: motivo = "Perfecto para tu hobby"

            resultados.append({"servicio": s, "score": score, "motivo": motivo})
        
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:10]

    def _predecir_score(self, uc, ue, uh, s):
        if not self.modelo: return 0.0
        mc, me, mh = (1 if uc in s.lista_comida else 0), (1 if ue in s.lista_estudio else 0), (1 if uh in s.lista_hobby else 0)
        maf_h = 1 if uh in AFINIDAD_HOBBY and set(s.lista_hobby).intersection(AFINIDAD_HOBBY[uh]) else 0
        features = [uc, ue, uh, mc, me, mh, maf_h, s.popularidad]
        df_input = pd.DataFrame([features], columns=['uc','ue','uh','mc','me','mh','maf_h','pop'])
        return float(self.modelo.predict(df_input)[0])