from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

# Importaciones locales
from database import engine, get_db
import models
from ml_engine import MotorRecomendacion

# Crear tablas al iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoliMapa Backend V3", version="Final")
recomendador = MotorRecomendacion()

# --- MODELOS DE DATOS (SCHEMAS) ---

class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

# Modelo para los pines AZULES (Edificios Generales)
class EdificioBasico(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    descripcion: str

# Modelo para los pines ROJOS (Servicios Recomendados)
class ServicioData(BaseModel):
    id_servicio: int
    nombre_servicio: str
    piso: str
    nombre_edificio: str
    lat: float
    lng: float
    categoria: str

class RecomendacionResponse(BaseModel):
    datos: ServicioData
    score: float
    motivo: str

class RespuestaRegistro(BaseModel):
    mensaje: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "PoliMapa Backend Online"}

@app.post("/registrar", response_model=RespuestaRegistro)
def registrar_usuario(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    
    if usuario:
        usuario.nombre = datos.nombre
        usuario.pref_comida = datos.preferencias.sel_comida
        usuario.pref_estudio = datos.preferencias.sel_estudio
        usuario.pref_hobby = datos.preferencias.sel_hobby
    else:
        nuevo_usuario = models.UsuarioDB(
            nombre=datos.nombre,
            email=datos.email,
            pref_comida=datos.preferencias.sel_comida,
            pref_estudio=datos.preferencias.sel_estudio,
            pref_hobby=datos.preferencias.sel_hobby
        )
        db.add(nuevo_usuario)
    
    db.commit()
    return {"mensaje": "Usuario guardado exitosamente"}

# NUEVO ENDPOINT: Obtener todos los edificios (Para pines Azules)
@app.get("/edificios", response_model=List[EdificioBasico])
def obtener_todos_los_edificios(db: Session = Depends(get_db)):
    edificios = db.query(models.EdificioDB).all()
    resultado = []
    for ed in edificios:
        resultado.append({
            "id": ed.id,
            "nombre": ed.nombre,
            "lat": ed.lat,
            "lng": ed.lng,
            "descripcion": ed.descripcion or "Edificio del campus"
        })
    return resultado

# ENDPOINT: Recomendaciones (Para pines Rojos)
@app.get("/recomendaciones/{email}", response_model=List[RecomendacionResponse])
def obtener_recomendaciones(email: str, db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    servicios = db.query(models.ServicioDB).join(models.EdificioDB).all()
    
    ranking = []
    for s in servicios:
        # Filtrar servicios vacíos
        if not (s.es_lugar_comida or s.es_lugar_estudio or s.es_lugar_hobby):
            continue

        score = recomendador.predecir(usuario, s)
        
        # Categorización visual
        categoria = "General"
        motivo = "Lugar de interés"
        
        if s.es_lugar_comida and usuario.pref_comida > 0:
            categoria = "Comida"
            motivo = "Recomendado para comer"
        elif s.es_lugar_estudio and usuario.pref_estudio > 0:
            categoria = "Estudio"
            motivo = "Ideal para estudiar"
        elif s.es_lugar_hobby and usuario.pref_hobby > 0:
            categoria = "Hobby"
            motivo = "Zona recreativa"
            
        if score > 40:
            ranking.append({
                "datos": {
                    "id_servicio": s.id,
                    "nombre_servicio": s.nombre,
                    "piso": s.piso or "PB",
                    "nombre_edificio": s.edificio.nombre,
                    "lat": s.edificio.lat,
                    "lng": s.edificio.lng,
                    "categoria": categoria
                },
                "score": score,
                "motivo": motivo
            })
    
    return sorted(ranking, key=lambda x: x["score"], reverse=True)[:15]