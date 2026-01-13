class MotorRecomendacion:
    def __init__(self):
        self.W_PREFERENCIA = 0.7 
        self.W_EVENTO = 0.3      

    def predecir(self, usuario, edificio, eventos_activos, ubicacion_usuario_lat=None, ubicacion_usuario_lng=None):
        score = 0.0
        
        # 1. ANALIZAR QUÉ TIENE EL EDIFICIO POR DENTRO
        # Iteramos sobre sus servicios para ver qué ofrece
        tiene_comida = any(s.es_lugar_comida for s in edificio.servicios_lista)
        tiene_estudio = any(s.es_lugar_estudio for s in edificio.servicios_lista)
        tiene_hobby = any(s.es_lugar_hobby for s in edificio.servicios_lista)
        
        # 2. MATCH CON USUARIO (Ahora comparamos con lo que encontramos arriba)
        
        # Si el edificio tiene comida Y al usuario le gusta (índice bajo en tu app era comida)
        if tiene_comida:
            # Asumimos que pref_comida viene de 0 a 3. Damos peso si seleccionó algo válido.
            if usuario.pref_comida is not None: score += 20

        if tiene_estudio:
            score += 20

        if tiene_hobby:
            score += 20

        # 3. MATCH CON EVENTOS (Esto se mantiene igual)
        match_evento = None
        if eventos_activos:
            score += 30 
            match_evento = eventos_activos[0]

        return score, match_evento