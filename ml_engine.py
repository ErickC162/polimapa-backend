import joblib
import pandas as pd
import os
from thefuzz import fuzz # Requiere: pip install thefuzz python-Levenshtein

class MotorRecomendacion:
    def __init__(self):
        # Carga el modelo de IA si existe
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None
        self.cols = ['u_comida', 'u_estudio', 'u_hobby', 'match_comida', 'match_estudio', 'match_hobby', 'match_afinidad', 'popularidad']

    def recomendar_servicios(self, u_c, u_e, u_h, servicios_db):
        res = []
        for s in servicios_db:
            score = self._predecir(u_c, u_e, u_h, s)
            motivo = "Lugar recomendado"
            if u_c in s.lista_comida: motivo = "Ideal para comer"
            elif u_e in s.lista_estudio: motivo = "Zona de estudio"
            elif u_h in s.lista_hobby: motivo = "Actividad recreativa"
            
            res.append({"servicio": s, "score": score, "motivo": motivo})
        
        # Ordenar por mejor puntuación
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:10]

    def buscar_edificios(self, query: str, edificios_db):
        """
        Función clave para el Autocompletado:
        Busca coincidencias en:
        1. Nombre del edificio
        2. Tags del edificio (keywords)
        3. Tags de los servicios DENTRO del edificio
        """
        resultados = []
        q = query.lower()
        for ed in edificios_db:
            # Score por nombre de edificio
            score_nombre = fuzz.token_set_ratio(q, ed.nombre.lower())
            
            # Score por keywords del edificio (si tiene)
            score_tags_ed = fuzz.token_set_ratio(q, ed.keywords.lower() if ed.keywords else "")
            
            # Score por keywords de sus servicios internos
            tags_internos = " ".join([s.keywords.lower() for s in ed.servicios if s.keywords])
            score_servicios = fuzz.token_set_ratio(q, tags_internos)
            
            # Nos quedamos con la mejor coincidencia
            score_final = max(score_nombre, score_tags_ed, score_servicios)
            
            # Si supera el umbral de similitud (45%), se agrega a resultados
            if score_final > 45:
                resultados.append({
                    "id": ed.id, 
                    "nombre": ed.nombre, 
                    "lat": ed.lat, 
                    "lng": ed.lng, 
                    "score": score_final
                })
        
        # Ordenamos para mostrar los más relevantes primero en el dropdown
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:8] # Retorna los top 8 para no saturar la lista

    def _predecir(self, uc, ue, uh, s):
        if not self.modelo: return float(s.popularidad)
        afinidad = {1:[2,3], 2:[1,3], 3:[1,2], 6:[3,4]}
        maf = 1 if uh in afinidad and set(s.lista_hobby).intersection(afinidad[uh]) else 0
        features = [uc, ue, uh, 1 if uc in s.lista_comida else 0, 1 if ue in s.lista_estudio else 0, 1 if uh in s.lista_hobby else 0, maf, s.popularidad]
        return float(self.modelo.predict(pd.DataFrame([features], columns=self.cols))[0])