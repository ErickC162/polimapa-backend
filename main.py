from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database import engine, get_db
import models
from ml_engine import MotorRecomendacion

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
recomendador = MotorRecomendacion()

# --- MODELOS JSON ---
class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

class ServicioResponse(BaseModel):
    id_servicio: int
    nombre_servicio: str
    piso: str
    nombre_edificio: str
    lat: float
    lng: float
    categoria: str

class RecomendacionFinal(BaseModel):
    datos: ServicioResponse
    score: float
    motivo: str

class Resp(BaseModel):
    mensaje: str

# --- ENDPOINTS ---
@app.post("/registrar", response_model=Resp)
def registrar(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    user = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == datos.email).first()
    if not user:
        user = models.UsuarioDB(email=datos.email)
        db.add(user)
    
    user.nombre = datos.nombre
    user.pref_comida = datos.preferencias.sel_comida
    user.pref_estudio = datos.preferencias.sel_estudio
    user.pref_hobby = datos.preferencias.sel_hobby
    db.commit()
    return {"mensaje": "OK"}

@app.get("/recomendaciones/{email}", response_model=List[RecomendacionFinal])
def recomendar(email: str, db: Session = Depends(get_db)):
    # 1. Buscar usuario
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Obtener TODOS los servicios
    servicios = db.query(models.ServicioDB).join(models.EdificioDB).all()
    
    ranking = []
    
    for serv in servicios:
        # 3. Predecir (Aquí los servicios "aburridos" sacarán score negativo o cero)
        score = recomendador.predecir(usuario, serv)
        
        # 4. Etiquetas
        cat = "General"
        motivo = "Ubicación EPN"
        
        if serv.es_lugar_comida and usuario.pref_comida > 0:
            cat = "Comida"
            motivo = "Recomendado para comer"
        elif serv.es_lugar_estudio and usuario.pref_estudio > 0:
            cat = "Estudio"
            motivo = "Ideal para estudiar"
        elif serv.es_lugar_hobby and usuario.pref_hobby > 0:
            cat = "Hobby"
            motivo = "Zona recreativa"
            
        # FILTRO: Solo devolver si el score es positivo (> 40)
        # Esto elimina automáticamente a Rectorado, Secretarías, etc.
        if score > 40:
            ranking.append({
                "datos": {
                    "id_servicio": serv.id,
                    "nombre_servicio": serv.nombre,
                    "piso": serv.piso or "PB",
                    "nombre_edificio": serv.edificio.nombre,
                    "lat": serv.edificio.lat,
                    "lng": serv.edificio.lng,
                    "categoria": cat
                },
                "score": score,
                "motivo": motivo
            })
            
    # Devolver Top 4
    return sorted(ranking, key=lambda x: x["score"], reverse=True)[:4]