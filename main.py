from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel

# --- IMPORTACIONES LOCALES (Asegúrate de tener database.py, models.py y ml_engine.py) ---
from database import engine, get_db, Base
import models
from ml_engine import MotorRecomendacion

# Crear tablas al iniciar
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoliMapa Backend", version="Final 5.0")
recomendador = MotorRecomendacion()

# --- SCHEMAS ---
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
    servicios: List[str] = []

class RecomendacionResponse(BaseModel):
    edificio: EdificioData
    score: float
    motivo: str

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "online"}

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
            nombre=datos.nombre, email=datos.email,
            pref_comida=datos.preferencias.sel_comida,
            pref_estudio=datos.preferencias.sel_estudio,
            pref_hobby=datos.preferencias.sel_hobby
        )
        db.add(usuario_db)
        msg = "Usuario registrado"
    db.commit()
    return {"mensaje": msg}

@app.get("/recomendaciones/{email}", response_model=List[RecomendacionResponse])
def obtener_mapa_inteligente(email: str, latitud: Optional[float] = Query(None), longitud: Optional[float] = Query(None), db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    edificios = db.query(models.EdificioDB).all()
    resultados = []

    for ed in edificios:
        eventos = db.query(models.EventoDB).filter(models.EventoDB.edificio_id == ed.id).all()
        score, evento_match = recomendador.predecir(usuario, ed, eventos, latitud, longitud)
        
        motivo = "Edificio del campus"
        if evento_match: motivo = f"🎉 Evento: {evento_match.nombre}"
        elif score >= 80: motivo = "🔥 ¡Muy recomendado!"
        elif score >= 50: motivo = "✅ Compatible contigo"

        resultados.append({
            "edificio": {
                "id": ed.id, "nombre": ed.nombre, 
                "lat": ed.lat, "lng": ed.lng, 
                "descripcion": ed.descripcion,
                "servicios": [s.nombre for s in ed.servicios_lista]
            },
            "score": score,
            "motivo": motivo
        })
    
    # Ordenamos por score descendente (los mejores primero)
    return sorted(resultados, key=lambda x: x["score"], reverse=True)

@app.get("/setup_datos_iniciales")
def setup_db(db: Session = Depends(get_db)):
    # ... (Aquí va el código de carga masiva de los 37 edificios que te pasé antes) ...
    # Si necesitas que te lo repita completo, avísame, pero es el mismo de la respuesta anterior.
    return {"msg": "Base de datos lista."}