import joblib
import pandas as pd
import os
from thefuzz import fuzz # Asegúrate de tener instalado: pip install thefuzz

class MotorRecomendacion:
    def __init__(self):
        # Carga el modelo de IA si existe, si no, funciona sin él (evita errores)
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        self.modelo = joblib.load(ruta) if os.path.exists(ruta) else None
        self.cols = ['u_comida', 'u_estudio', 'u_hobby', 'match_comida', 'match_estudio', 'match_hobby', 'match_afinidad', 'popularidad']

    def recomendar_servicios(self, u_c, u_e, u_h, servicios_db):
        res = []
        for s in servicios_db:
            score = self._predecir(u_c, u_e, u_h, s)
            motivo = "Lugar popular"
            if u_c in s.lista_comida: motivo = "Buena comida"
            elif u_e in s.lista_estudio: motivo = "Zona de estudio"
            elif u_h in s.lista_hobby: motivo = "Recreación"
            
            res.append({"servicio": s, "score": score, "motivo": motivo})
        
        res.sort(key=lambda x: x["score"], reverse=True)
        return res[:10]

    def buscar_mixto(self, query: str, edificios_db, servicios_db):
        """
        Busca en Edificios y Servicios y devuelve una estructura segura 
        que el celular puede leer sin crashear.
        """
        resultados = []
        q = query.lower()

        # 1. BÚSQUEDA EN EDIFICIOS