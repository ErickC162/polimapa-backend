import joblib
import pandas as pd
import os
from models import UsuarioDB, EdificioDB, EventoDB

class MotorRecomendacion:
    def __init__(self):
        # Cargamos el cerebro al iniciar el servidor
        # Buscamos el archivo en la misma carpeta que este script
        ruta_modelo = os.path.join(os.path.dirname(__file__), 'polimapa_brain.joblib')
        
        try:
            self.modelo = joblib.load(ruta_modelo)
            print("✅ Cerebro de IA cargado correctamente.")
        except Exception as e:
            print(f"⚠️ Error cargando modelo IA: {e}")
            self.modelo = None

        # DICCIONARIO DE CARACTERÍSTICAS (Metadata)
        # Esto es vital: El modelo necesita saber qué tipo de comida/hobby tiene cada edificio
        # Copiamos la lógica que usaste para generar el dataset.
        # ID Edificio -> [e_comida, e_estudio, e_hobby]
        self.meta_edificios = {
            1: (-1, -1, 5),   # Teatro
            2: (-1, -1, 5),   # Museo
            3: (-1, -1, -1),  # Admin
            4: (-1, -1, 5),   # Casa Patrimonial
            5: (-1, 3, -1),   # CIV
            6: (1, 1, -1),    # Civil
            7: (-1, 3, -1),   # Nuclear
            8: (-1, 3, -1),   # Aguas
            9: (-1, -1, -1),
            10: (-1, 3, -1),
            11: (-1, 3, -1),
            12: (2, 4, -1),   # Ciencias
            13: (1, 1, -1),   # Geología
            14: (0, 4, 2),    # Básica
            15: (1, 3, 3),    # Mecánica
            16: (1, 3, 3),    # Eléctrica
            17: (-1, 3, -1),
            18: (-1, 3, -1),
            19: (2, 3, -1),   # Alimentos
            20: (1, 3, 3),    # Sistemas (FIS)
            21: (3, 3, -1),   # ESFOT
            22: (-1, 3, -1),
            23: (-1, 2, 5),   # Plaza EARME
            24: (-1, 4, -1),
            25: (-1, 3, -1),
            26: (-1, 3, -1),
            27: (3, 0, 5),    # EARME Admin
            28: (-1, 3, -1),
            29: (-1, -1, -1),
            30: (-1, 2, 0),   # Estadio
            31: (-1, -1, 1),  # Canchas
            32: (-1, -1, 0),  # Mecánica Cancha
            33: (-1, 2, 5),   # Ágora
            34: (-1, -1, -1),
            35: (-1, -1, 5),  # Coro
            36: (-1, -1, -1),
            37: (-1, -1, 4)   # Gym
        }

    def predecir(self, usuario: UsuarioDB, edificio: EdificioDB, eventos: list[EventoDB], lat=None, lng=None) -> tuple[float, EventoDB]:
        score = 0.0
        evento_match = None
        
        # 1. PRIORIDAD ABSOLUTA: EVENTOS
        # Si hay un evento hoy, el modelo IA pasa a segundo plano
        if eventos:
            score = 100.0
            evento_match = eventos[0]
            return score, evento_match

        # 2. Si no hay modelo cargado, devolvemos 0 (Fail-safe)
        if self.modelo is None:
            return 0.0, None

        # 3. PREPARAR DATOS PARA LA IA
        # Necesitamos el vector: [u_comida, u_estudio, u_hobby, e_comida, e_estudio, e_hobby]
        
        # Datos del Usuario
        u_inputs = [usuario.pref_comida, usuario.pref_estudio, usuario.pref_hobby]
        
        # Datos del Edificio (Los sacamos del diccionario por ID)
        # Si el ID no está en la lista, asumimos (-1, -1, -1)
        e_inputs = self.meta_edificios.get(edificio.id, (-1, -1, -1))
        
        # Vector final (6 números)
        vector_entrada = [u_inputs + list(e_inputs)]
        
        # Nombre de las columnas para evitar warnings de sklearn
        columnas = ['u_comida', 'u_estudio', 'u_hobby', 'e_comida', 'e_estudio', 'e_hobby']
        df_entrada = pd.DataFrame(vector_entrada, columns=columnas)

        # 4. ¡PREDECIR!
        prediccion = self.modelo.predict(df_entrada)[0]
        
        # Ajuste fino: Sumar un poco si está muy cerca (opcional)
        if lat and lng:
            dist = ((edificio.lat - lat)**2 + (edificio.lng - lng)**2)**0.5
            if dist < 0.002:
                prediccion += 5.0

        return float(prediccion), None