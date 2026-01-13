from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# --- IMPORTACIONES LOCALES ---
from database import engine, get_db, Base
import models
from ml_engine import MotorRecomendacion

# 1. Crear las tablas al iniciar
models.Base.metadata.create_all(bind=engine)

# 2. INICIALIZAR LA APP (¡Esto es lo que faltaba o estaba mal ubicado!)
app = FastAPI(title="PoliMapa Backend", version="3.0 Servicios Relacionales")

# 3. Inicializar el motor de IA
recomendador = MotorRecomendacion()

# --- SCHEMAS (Modelos de Datos para JSON) ---

class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

class EdificioData(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    descripcion: str
    servicios: List[str] = [] # Lista de nombres de servicios

class RecomendacionResponse(BaseModel):
    edificio: EdificioData
    score: float
    motivo: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online", "version": "3.0"}

@app.post("/registrar")
def registrar_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    usuario_db = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    
    if usuario_db:
        # Actualizar
        usuario_db.nombre = datos.nombre
        usuario_db.pref_comida = datos.preferencias.sel_comida
        usuario_db.pref_estudio = datos.preferencias.sel_estudio
        usuario_db.pref_hobby = datos.preferencias.sel_hobby
        msg = "Usuario actualizado"
    else:
        # Crear
        usuario_db = models.UsuarioDB(
            nombre=datos.nombre,
            email=datos.email,
            pref_comida=datos.preferencias.sel_comida,
            pref_estudio=datos.preferencias.sel_estudio,
            pref_hobby=datos.preferencias.sel_hobby
        )
        db.add(usuario_db)
        msg = "Usuario registrado"
    
    db.commit()
    return {"mensaje": msg}

@app.get("/recomendaciones/{email}", response_model=List[RecomendacionResponse])
def obtener_recomendaciones(
    email: str,
    latitud: Optional[float] = Query(None),
    longitud: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    # 1. Buscar Usuario
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Buscar Edificios
    edificios = db.query(models.EdificioDB).all()
    resultados_procesados = []

    # 3. Analizar cada edificio
    for ed in edificios:
        eventos = db.query(models.EventoDB).filter(models.EventoDB.edificio_id == ed.id).all()
        
        # El motor ahora buscará etiquetas DENTRO de los servicios del edificio
        score_ia, evento_match = recomendador.predecir(
            usuario=usuario, 
            edificio=ed, 
            eventos_activos=eventos,
            ubicacion_usuario_lat=latitud, 
            ubicacion_usuario_lng=longitud
        )
        
        motivo = "Basado en tus preferencias"
        if evento_match:
            motivo = f"🎉 ¡Evento!: {evento_match.nombre}"
        elif score_ia >= 80:
            motivo = "🔥 Coincidencia perfecta"
        elif score_ia >= 50:
            motivo = "✅ Recomendado para ti"

        # Extraemos solo los nombres de los servicios para enviarlos a Android
        nombres_servicios = [s.nombre for s in ed.servicios_lista]

        if score_ia > 15.0:
            resultados_procesados.append({
                "edificio": {
                    "id": ed.id, 
                    "nombre": ed.nombre, 
                    "lat": ed.lat, 
                    "lng": ed.lng, 
                    "descripcion": ed.descripcion,
                    "servicios": nombres_servicios
                },
                "score": score_ia,
                "motivo": motivo
            })
    
    # Retornar Top 3
    return sorted(resultados_procesados, key=lambda x: x["score"], reverse=True)[:3]

# --- ENDPOINTS DE GESTIÓN (RESET Y SETUP) ---

@app.get("/reset_db_completo")
def reset_database(db: Session = Depends(get_db)):
    """
    Borra y recrea las tablas. Necesario porque cambiamos la estructura en models.py
    """
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    return {"msg": "Base de datos formateada. Estructura nueva aplicada."}

@app.get("/setup_datos_iniciales")
def setup_db(db: Session = Depends(get_db)):
    if db.query(models.EdificioDB).first():
        return {"msg": "La base de datos ya tiene datos."}
    
    # 1. Crear Edificios (NEUTROS, sin etiquetas booleanas aquí)
    biblio = models.EdificioDB(nombre="Biblioteca Central", lat=-0.2110, lng=-78.4910, descripcion="Zona de silencio.")
    comedor = models.EdificioDB(nombre="Comedor Politécnico", lat=-0.2100, lng=-78.4900, descripcion="Almuerzos.")
    aso = models.EdificioDB(nombre="Aso Sistemas", lat=-0.2120, lng=-78.4920, descripcion="Gaming y PC.")
    
    db.add_all([biblio, comedor, aso])
    db.commit() # Guardar para generar IDs
    
    # 2. Crear Servicios (AQUÍ van las etiquetas booleanas)
    servicios = [
        # Biblioteca: Es de estudio
        models.ServicioDB(nombre="Cubículos", edificio_id=biblio.id, es_lugar_estudio=True),
        models.ServicioDB(nombre="Wifi", edificio_id=biblio.id, es_lugar_estudio=True),
        
        # Comedor: Es de comida
        models.ServicioDB(nombre="Almuerzos", edificio_id=comedor.id, es_lugar_comida=True),
        
        # Aso Sistemas: Es mixto (Comida + Hobby + Estudio)
        models.ServicioDB(nombre="Bar de Snacks", edificio_id=aso.id, es_lugar_comida=True),
        models.ServicioDB(nombre="Arcade", edificio_id=aso.id, es_lugar_hobby=True),
        models.ServicioDB(nombre="Impresiones", edificio_id=aso.id, es_lugar_estudio=True)
    ]
    
    db.add_all(servicios)
    
    # 3. Crear Evento
    ev = models.EventoDB(nombre="Torneo FC26", edificio_id=aso.id, tipo_evento="hobby")
    db.add(ev)
    
    db.commit()
    return {"msg": "Datos cargados: Etiquetas asignadas a Servicios correctamente."}