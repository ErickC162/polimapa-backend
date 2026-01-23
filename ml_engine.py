import joblib
import pandas as pd
import os

# Definimos la afinidad aquí también para usarla en tiempo real
AFINIDAD_HOBBY = {
    1: [2, 3],
    2: [1, 3],
    3: [1, 2],
    6: [3, 4]
}

class MotorRecomendacion:
    def __init__(self):
        ruta = os.path.join(os.path.dirname(__file__), 'polimapa_brain_servicios.joblib')
        try:
            self.modelo = joblib.load(ruta)
            print("Motor ML cargado (Modo Categorías Específicas).")
        except:
            print("No se encontró modelo. Usando valor 0 por defecto.")
            self.modelo = None

    def predecir(self, usuario, servicio_db):
        """
        usuario: Objeto UsuarioDB (o dict) con pref_comida, pref_estudio, pref_hobby
        servicio_db: Objeto ServicioDB con las propiedades .lista_comida, .lista_estudio, etc.
        """
        if not self.modelo:
            return 0

        # 1. Inputs del Usuario
        uc = usuario.pref_comida or 0
        ue = usuario.pref_estudio or 0
        uh = usuario.pref_hobby or 0
        
        # 2. Inputs del Servicio (Extracción desde las nuevas columnas)
        # Usamos las properties definidas en models.py que devuelven listas [1, 2]
        c_c = servicio_db.lista_comida
        c_e = servicio_db.lista_estudio
        c_h = servicio_db.lista_hobby
        pop = servicio_db.popularidad or 5

        # 3. Ingeniería de Características (Feature Engineering en Tiempo Real)
        # Calculamos si hay match exacto
        mc = 1 if uc in c_c else 0
        me = 1 if ue in c_e else 0
        mh = 1 if uh in c_h else 0
        
        # Calculamos match por afinidad
        maf_h = 0
        if uh in AFINIDAD_HOBBY and set(c_h).intersection(AFINIDAD_HOBBY[uh]):
            maf_h = 1
            
        # 4. Construir DataFrame para el modelo
        # El orden de columnas debe ser IDÉNTICO al de generar_datos.py
        cols = ['uc','ue','uh','mc','me','mh','maf_h','pop']
        features = [uc, ue, uh, mc, me, mh, maf_h, pop]
        
        df_input = pd.DataFrame([features], columns=cols)
        
        # 5. Predecir
        score_predicho = float(self.modelo.predict(df_input)[0])
        return score_predicho