import joblib
import pandas as pd
import os

AFINIDAD_HOBBY = {1: [2, 3], 2: [1, 3], 3: [1, 2], 6: [3, 4]}

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None

    def recomendar_servicios(self, u_c, u_e, u_h, servicios_db):
        resultados = []
        for s in servicios_db:
            score = self._predecir(u_c, u_e, u_h, s)
            motivo = "Sugerencia basada en popularidad"
            if u_c in s.lista_comida: motivo = "Coincide con tus gustos de comida"
            elif u_e in s.lista_estudio: motivo = "Ideal para estudiar"
            elif u_h in s.lista_hobby: motivo = "Perfecto para tu hobby"
            
            resultados.append({"servicio": s, "score": score, "motivo": motivo})
        
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:10]

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return 0.0
        mc, me, mh = (1 if uc in s.lista_comida else 0), (1 if ue in s.lista_estudio else 0), (1 if uh in s.lista_hobby else 0)
        maf_h = 1 if uh in AFINIDAD_HOBBY and set(s.lista_hobby).intersection(AFINIDAD_HOBBY[uh]) else 0
        df = pd.DataFrame([[uc, ue, uh, mc, me, mh, maf_h, s.popularidad]], columns=['uc','ue','uh','mc','me','mh','maf_h','pop'])
        return float(self.modelo.predict(df)[0])