from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# --- IMPORTACIONES LOCALES (Tu Arquitectura) ---
from database import engine, get_db, Base
import models
from ml_engine import MotorRecomendacion

# 1. Crear las tablas en la Base de Datos si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoliMapa Backend", version="2.0")

# 2. Instanciar el Motor de IA (Se carga una sola vez en memoria)
recomendador = MotorRecomendacion()

# --- SCHEMAS (Validación de datos JSON entrada/salida) ---

# Para recibir las preferencias anidadas desde Android
class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

# Para responder al mapa con datos limpios
class EdificioData(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    descripcion: str

class RecomendacionResponse(BaseModel):
    edificio: EdificioData
    score: float
    motivo: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online", "mode": "PostgreSQL + ML Engine"}

@app.post("/registrar")
def registrar_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    """
    Recibe el usuario desde Android y lo guarda/actualiza en PostgreSQL.
    Aplana el objeto 'preferencias' para guardarlo en columnas simples.
    """
    # 1. Buscar si ya existe por email
    usuario_db = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    
    if usuario_db:
        # Actualizar existentes
        usuario_db.nombre = datos.nombre
        usuario_db.pref_comida = datos.preferencias.sel_comida
        usuario_db.pref_estudio = datos.preferencias.sel_estudio
        usuario_db.pref_hobby = datos.preferencias.sel_hobby
        msg = "Usuario actualizado"
    else:
        # Crear nuevo
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
    db.refresh(usuario_db)
    return {"mensaje": msg, "usuario": usuario_db.nombre}

@app.get("/recomendaciones/{email}", response_model=List[RecomendacionResponse])
def obtener_recomendaciones(
    email: str,
    latitud: Optional[float] = Query(None), # Opcionales por si Android no envía GPS aún
    longitud: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    El núcleo del sistema.
    1. Busca al usuario.
    2. Busca edificios y eventos.
    3. Usa ml_engine para calcular scores.
    4. Retorna el Top 3.
    """
    # A. Validar Usuario
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        # Si no existe, lanzamos error 404 para que Android lo sepa
        raise HTTPException(status_code=404, detail="Usuario no encontrado. Regístrate primero.")

    # B. Obtener todos los Edificios
    edificios = db.query(models.EdificioDB).all()
    
    resultados_procesados = []

    # C. Iterar y Predecir
    for ed in edificios:
        # Buscar eventos activos en este edificio específico
        eventos = db.query(models.EventoDB).filter(models.EventoDB.edificio_id == ed.id).all()
        
        # LLAMADA AL MOTOR DE IA
        score_ia, evento_match = recomendador.predecir(
            usuario=usuario, 
            edificio=ed, 
            eventos_activos=eventos,
            ubicacion_usuario_lat=latitud,
            ubicacion_usuario_lng=longitud
        )
        
        # Generar texto explicativo (Explainability)
        motivo = "Basado en tus preferencias generales"
        if evento_match:
            motivo = f"🎉 ¡Evento ahora!: {evento_match.nombre}"
        elif score_ia >= 80:
            motivo = "🔥 Coincidencia perfecta con tus gustos"
        elif score_ia >= 50:
            motivo = "✅ Recomendado para ti"

        # D. Filtrar ruido (Solo mostramos si tiene un score mínimo decente)
        if score_ia > 15.0:
            resultados_procesados.append({
                "edificio": {
                    "id": ed.id, 
                    "nombre": ed.nombre, 
                    "lat": ed.lat, 
                    "lng": ed.lng, 
                    "descripcion": ed.descripcion
                },
                "score": score_ia,
                "motivo": motivo
            })
    
    # E. Ordenar (Mayor puntaje primero) y cortar (Top 3)
    resultados_ordenados = sorted(resultados_procesados, key=lambda x: x["score"], reverse=True)
    top_3 = resultados_ordenados[:3]
    
    return top_3

# --- HERRAMIENTAS DE CONFIGURACIÓN ---

@app.get("/setup_datos_iniciales")
def setup_db(db: Session = Depends(get_db)):
    """
    Ejecuta esto UNA VEZ desde el navegador para llenar la base de datos vacía.
    """
    if db.query(models.EdificioDB).first():
        return {"msg": "La base de datos ya tiene datos. No se hizo nada."}
    
    # 1. Crear Edificios con sus 'Features' para el Random Forest
    edificios_seed = [
        models.EdificioDB(
            nombre="Comedor Politécnico", 
            lat=-0.2100, lng=-78.4900, 
            descripcion="Almuerzos y comida variada.",
            es_lugar_comida=True, es_lugar_estudio=False, es_lugar_hobby=False
        ),
        models.EdificioDB(
            nombre="Biblioteca Central", 
            lat=-0.2110, lng=-78.4910, 
            descripcion="Zona de silencio y lectura.",
            es_lugar_comida=False, es_lugar_estudio=True, es_lugar_hobby=False
        ),
        models.EdificioDB(
            nombre="Canchas Sintéticas", 
            lat=-0.2130, lng=-78.4930, 
            descripcion="Fútbol y deporte al aire libre.",
            es_lugar_comida=False, es_lugar_estudio=False, es_lugar_hobby=True
        ),
        models.EdificioDB(
            nombre="Asociación de Sistemas", 
            lat=-0.2120, lng=-78.4920, 
            descripcion="Gaming, descanso y computadoras.",
            es_lugar_comida=True, es_lugar_estudio=True, es_lugar_hobby=True
        ),
        models.EdificioDB(
            nombre="Edificio de Aulas (EARME)", 
            lat=-0.2140, lng=-78.4940, 
            descripcion="Clases teóricas.",
            es_lugar_comida=False, es_lugar_estudio=True, es_lugar_hobby=False
        )
    ]
    
    db.add_all(edificios_seed)
    db.commit()
    
    # 2. Crear un Evento de prueba
    # Asumimos que la Aso de Sistemas es el ID 4 (según el orden de arriba, pero buscamos para asegurar)
    aso = db.query(models.EdificioDB).filter(models.EdificioDB.nombre == "Asociación de Sistemas").first()
    if aso:
        evento = models.EventoDB(
            nombre="Torneo FC26", 
            edificio_id=aso.id, 
            tipo_evento="hobby"
        )
        db.add(evento)
        db.commit()
    
    return {"msg": "¡Base de datos inicializada con éxito! Edificios y eventos creados."}