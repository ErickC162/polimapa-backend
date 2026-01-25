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
        """Busca en edificios y servicios, devolviendo una lista de diccionarios planos"""
        resultados = []
        q = query.lower()

        # 1. Buscar en EDIFICIOS
        for ed in edificios_db:
            # Manejo seguro de nulos en keywords y nombres
            nombre_str = ed.nombre.lower() if ed.nombre else ""
            keys_str = ed.keywords.lower() if ed.keywords else ""
            
            score_nom = fuzz.token_set_ratio(q, nombre_str)
            score_key = fuzz.token_set_ratio(q, keys_str)
            score = float(max(score_nom, score_key)) # Asegurar que es float
            
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

        # 2. Buscar en SERVICIOS
        for s in servicios_db:
            if not s.edificio: continue # Saltar servicios huérfanos si los hubiera

            nombre_str = s.nombre.lower() if s.nombre else ""
            keys_str = s.keywords.lower() if s.keywords else ""

            score_nom = fuzz.token_set_ratio(q, nombre_str)
            score_key = fuzz.token_set_ratio(q, keys_str)
            score = float(max(score_nom, score_key))

            if score > 45:
                # Restamos 1 punto para priorizar el edificio en caso de empate
                resultados.append({
                    "id": s.id,
                    "nombre": s.nombre,
                    "tipo": "Servicio",
                    "lat": s.edificio.lat,
                    "lng": s.edificio.lng,
                    "info_extra": f"En: {s.edificio.nombre}",
                    "score": score - 1.0
                })

        # Ordenar por score descendente y tomar los mejores 12
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:12]

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return float(s.popularidad)
        try:
            features = [uc, ue, uh, 1 if uc in s.lista_comida else 0, 1 if ue in s.lista_estudio else 0, 1 if uh in s.lista_hobby else 0, 0, s.popularidad]
            return float(self.modelo.predict(pd.DataFrame([features], columns=self.cols))[0])
        except Exception:
            return float(s.popularidad) # Fallback seguro