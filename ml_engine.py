import math

class MotorRecomendacion:
    def __init__(self):
        # Pesos calibrados (Hiperparámetros iniciales)
        # En el futuro, un algoritmo de regresión ajustará esto solo.
        self.W_PREFERENCIA = 0.6  # Qué tanto importa el gusto del usuario
        self.W_EVENTO = 0.3       # Qué tanto importa si hay un evento
        self.W_DISTANCIA = 0.1    # (Opcional) Qué tanto importa la cercanía

    def _calcular_similitud_coseno(self, v_usuario: list, v_edificio: list) -> float:
        """
        Calcula qué tan alineados están los gustos del usuario con lo que ofrece el edificio.
        Matemática vectorial robusta.
        """
        dot_product = sum(u * e for u, e in zip(v_usuario, v_edificio))
        # Como nuestros vectores son binarios/normalizados simplificados, 
        # el producto punto es una excelente aproximación de similitud.
        return dot_product

    def _calcular_distancia_haversine(self, lat1, lon1, lat2, lon2):
        """
        Calcula distancia real en metros entre dos coordenadas (Fórmula Haversine).
        """
        R = 6371000 # Radio de la tierra en metros
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def predecir(self, usuario, edificio, eventos_activos, ubicacion_usuario_lat=None, ubicacion_usuario_lng=None):
        """
        Genera un Score (0 a 100) de recomendación.
        """
        
        # 1. FEATURE ENGINEERING (Convertir datos a vectores numéricos)
        # Convertimos las preferencias (0, 1, 2, 3...) a una escala 0.0 - 1.0
        # Asumiendo que en la encuesta el max valor era 5.
        vec_usuario = [
            (usuario.pref_comida or 0) / 5.0,
            (usuario.pref_estudio or 0) / 5.0,
            (usuario.pref_hobby or 0) / 5.0
        ]

        vec_edificio = [
            1.0 if edificio.es_lugar_comida else 0.0,
            1.0 if edificio.es_lugar_estudio else 0.0,
            1.0 if edificio.es_lugar_hobby else 0.0
        ]

        # 2. CÁLCULO DE AFINIDAD (Content-Based Filtering)
        score_afinidad = self._calcular_similitud_coseno(vec_usuario, vec_edificio)
        # Normalizamos para que no exceda 1.0
        score_afinidad = min(score_afinidad, 1.0)

        # 3. CONTEXTO (Eventos)
        score_contexto = 0.0
        match_evento = None
        if eventos_activos:
            # Si hay evento, analizamos si el evento coincide con gustos
            for evento in eventos_activos:
                # Si el evento es tipo 'hobby' y al usuario le gusta el hobby
                tipo = evento.tipo_evento # asumiendo string "comida", "estudio", "hobby"
                
                boost = 0.5 # Boost base por haber evento
                if tipo == "comida" and vec_usuario[0] > 0.6: boost = 1.0
                if tipo == "estudio" and vec_usuario[1] > 0.6: boost = 1.0
                if tipo == "hobby" and vec_usuario[2] > 0.6: boost = 1.0
                
                if boost > score_contexto:
                    score_contexto = boost
                    match_evento = evento

        # 4. DISTANCIA (Opcional - Penalización)
        factor_distancia = 1.0
        if ubicacion_usuario_lat and ubicacion_usuario_lng:
            dist_metros = self._calcular_distancia_haversine(
                ubicacion_usuario_lat, ubicacion_usuario_lng,
                edificio.lat, edificio.lng
            )
            # Si está a más de 500m, el interés baja gradualmente
            if dist_metros > 500:
                factor_distancia = max(0.5, 1 - (dist_metros - 500)/1000)

        # 5. ENSAMBLAJE FINAL (Weighted Sum Model)
        score_final = (score_afinidad * self.W_PREFERENCIA) + \
                      (score_contexto * self.W_EVENTO)
        
        score_final = score_final * factor_distancia

        # Convertir a escala 0-100 para fácil lectura
        return score_final * 100, match_evento