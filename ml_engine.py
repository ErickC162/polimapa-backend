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
            res.append({"servicio": s, "score": score, "motivo": "Recomendado"})
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:10]

    def buscar_mixto(self, query: str, edificios_db, servicios_db):
        resultados = []
        q = query.lower()

        # 1. Buscar en Edificios
        for ed in edificios_db:
            score_nom = fuzz.token_set_ratio(q, ed.nombre.lower())
            score_key = fuzz.token_set_ratio(q, ed.keywords.lower() if ed.keywords else "")
            score = max(score_nom, score_key)
            
            if score > 45:
                resultados.append({
                    "id": ed.id,
                    "nombre": ed.nombre,
                    "tipo": "Edificio",
                    "lat": ed.lat,
                    "lng": ed.lng,
                    "info_extra": "Campus EPN",
                    "score": score
                })

        # 2. Buscar en Servicios
        for s in servicios_db:
            score_nom = fuzz.token_set_ratio(q, s.nombre.lower())
            score_key = fuzz.token_set_ratio(q, s.keywords.lower() if s.keywords else "")
            score = max(score_nom, score_key)

            if score > 45:
                # Penalizamos levemente servicios vs edificios si el score es igual
                resultados.append({
                    "id": s.id,
                    "nombre": s.nombre,
                    "tipo": "Servicio",
                    "lat": s.edificio.lat,
                    "lng": s.edificio.lng,
                    "info_extra": f"En: {s.edificio.nombre}, {s.piso}",
                    "score": score - 1 
                })

        # Ordenar por score descendente
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:12] # Top 12 resultados

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return float(s.popularidad)
        features = [uc, ue, uh, 1 if uc in s.lista_comida else 0, 1 if ue in s.lista_estudio else 0, 1 if uh in s.lista_hobby else 0, 0, s.popularidad]
        return float(self.modelo.predict(pd.DataFrame([features], columns=self.cols))[0])