import joblib
import pandas as pd
import os
from thefuzz import fuzz

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None
        self.cols = ['u_comida', 'u_estudio', 'u_hobby', 'match_comida', 'match_estudio', 'match_hobby', 'match_afinidad', 'popularidad']

    def recomendar_servicios(self, u_c, u_e, u_h, servicios_db):
        res = []
        for s in servicios_db:
            score = self._predecir(u_c, u_e, u_h, s)
            motivo = "Recomendado"
            res.append({"servicio": s, "score": score, "motivo": motivo})
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:10]

    def buscar_edificios(self, query: str, edificios_db):
        """Busca edificios basándose en su nombre y en sus keywords."""
        resultados = []
        q = query.lower()
        for ed in edificios_db:
            # Score por nombre de edificio
            score_nombre = fuzz.token_set_ratio(q, ed.nombre.lower())
            # Score por sus keywords
            score_keys = fuzz.token_set_ratio(q, ed.keywords.lower() if ed.keywords else "")
            
            score_final = max(score_nombre, score_keys)
            if score_final > 45:
                resultados.append({
                    "id": ed.id, 
                    "nombre": ed.nombre, 
                    "lat": ed.lat, 
                    "lng": ed.lng, 
                    "score": score_final
                })
        
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:8]

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return float(s.popularidad)
        features = [uc, ue, uh, 1 if uc in s.lista_comida else 0, 1 if ue in s.lista_estudio else 0, 1 if uh in s.lista_hobby else 0, 0, s.popularidad]
        return float(self.modelo.predict(pd.DataFrame([features], columns=self.cols))[0])