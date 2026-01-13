from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# --- IMPORTACIONES LOCALES ---
from database import engine, get_db, Base
import models
from ml_engine import MotorRecomendacion

# Crear tablas si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoliMapa Backend", version="2.1 Servicios")
recomendador = MotorRecomendacion()

# --- SCHEMAS ACTUALIZADOS ---

class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

# AHORA EL EDIFICIO INCLUYE UNA LISTA DE STRINGS
class EdificioData(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    descripcion: str
    servicios: List[str] = [] # <--- Nuevo campo: Lista de servicios

class RecomendacionResponse(BaseModel):
    edificio: EdificioData
    score: float
    motivo: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online", "version": "2.1 con Servicios"}

# ... (El endpoint /registrar queda IGUAL que antes) ...
@app.post("/registrar")
def registrar_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    usuario_db = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    if usuario_db:
        usuario_db.nombre = datos.nombre
        usuario_db.pref_comida = datos.preferencias.sel_comida
        usuario_db.pref_estudio = datos.preferencias.sel_estudio
        usuario_db.pref_hobby = datos.preferencias.sel_hobby
        msg = "Usuario actualizado"
    else:
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
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    edificios = db.query(models.EdificioDB).all()
    resultados_procesados = []

    for ed in edificios:
        eventos = db.query(models.EventoDB).filter(models.EventoDB.edificio_id == ed.id).all()
        
        score_ia, evento_match = recomendador.predecir(
            usuario=usuario, edificio=ed, eventos_activos=eventos,
            ubicacion_usuario_lat=latitud, ubicacion_usuario_lng=longitud
        )
        
        motivo = "Basado en tus preferencias"
        if evento_match: motivo = f"🎉 ¡Evento!: {evento_match.nombre}"
        elif score_ia >= 80: motivo = "🔥 Coincidencia perfecta"
        elif score_ia >= 50: motivo = "✅ Recomendado para ti"

        # TRUCO: Convertimos la lista de objetos ServicioDB a lista de Strings simple para Android
        lista_servicios_nombres = [s.nombre for s in ed.servicios_lista]

        if score_ia > 15.0:
            resultados_procesados.append({
                "edificio": {
                    "id": ed.id, 
                    "nombre": ed.nombre, 
                    "lat": ed.lat, 
                    "lng": ed.lng, 
                    "descripcion": ed.descripcion,
                    "servicios": lista_servicios_nombres # <--- Enviamos la lista
                },
                "score": score_ia,
                "motivo": motivo
            })
    
    return sorted(resultados_procesados, key=lambda x: x["score"], reverse=True)[:3]

# --- NUEVOS ENDPOINTS DE GESTIÓN ---

@app.get("/reset_db_completo")
def reset_database(db: Session = Depends(get_db)):
    """
    ¡PELIGRO! Borra TODAS las tablas y las crea de nuevo.
    Úsalo solo cuando cambies la estructura de la BD (como hoy).
    """
    models.Base.metadata.drop_all(bind=engine)   # Borrar todo
    models.Base.metadata.create_all(bind=engine) # Crear todo limpio
    return {"msg": "Base de datos formateada a cero. Ahora ejecuta /setup_datos_iniciales"}

@app.get("/setup_datos_iniciales")
def setup_db(db: Session = Depends(get_db)):
    if db.query(models.EdificioDB).first():
        return {"msg": "La base de datos ya tiene datos."}
    
    # 1. Crear Edificio
    biblio = models.EdificioDB(
        nombre="Biblioteca Central", lat=-0.2110, lng=-78.4910, 
        descripcion="Zona de silencio.", es_lugar_estudio=True
    )
    comedor = models.EdificioDB(
        nombre="Comedor Politécnico", lat=-0.2100, lng=-78.4900, 
        descripcion="Almuerzos.", es_lugar_comida=True
    )
    aso = models.EdificioDB(
        nombre="Aso Sistemas", lat=-0.2120, lng=-78.4920, 
        descripcion="Gaming y PC.", es_lugar_hobby=True, es_lugar_estudio=True
    )
    
    db.add_all([biblio, comedor, aso])
    db.commit() # Guardamos para generar IDs
    
    # 2. Agregar Servicios (Aquí está la magia variable)
    servicios = [
        models.ServicioDB(nombre="Wifi Rápido", edificio_id=biblio.id),
        models.ServicioDB(nombre="Cubículos Privados", edificio_id=biblio.id),
        models.ServicioDB(nombre="Baños", edificio_id=biblio.id),
        
        models.ServicioDB(nombre="Microondas", edificio_id=comedor.id),
        models.ServicioDB(nombre="Lavamanos", edificio_id=comedor.id),
        
        models.ServicioDB(nombre="Computadoras", edificio_id=aso.id),
        models.ServicioDB(nombre="Arcade", edificio_id=aso.id),
        models.ServicioDB(nombre="Impresiones", edificio_id=aso.id)
    ]
    
    db.add_all(servicios)
    
    # 3. Eventos
    ev = models.EventoDB(nombre="Torneo FC26", edificio_id=aso.id, tipo_evento="hobby")
    db.add(ev)
    
    db.commit()
    return {"msg": "Datos cargados con Servicios variables"}