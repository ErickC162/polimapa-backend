from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, ml_engine
from typing import List

app = FastAPI(title="PoliMapa API")

@app.get("/")
def read_root():
    return {"mensaje": "PoliMapa API Funcionando"}

@app.post("/registrar", response_model=models.RespuestaRegistro)
def registrar(usuario: models.UsuarioRegistro, db: Session = Depends(database.get_db)):
    db_u = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if not db_u:
        db_u = models.Usuario(email=usuario.email, nombre=usuario.nombre)
        db.add(db_u)
    
    db_u.pref_comida = usuario.preferencias.sel_comida
    db_u.pref_estudio = usuario.preferencias.sel_estudio
    db_u.pref_hobby = usuario.preferencias.sel_hobby
    db.commit()
    return {"mensaje": "Sincronización exitosa"}

@app.get("/buscar", response_model=List[models.RecomendacionResponse])
def buscar(q: str, db: Session = Depends(database.get_db)):
    """Endpoint para búsqueda inteligente por texto"""
    if not q:
        return []
        
    motor = ml_engine.MotorRecomendacion()
    servicios = db.query(models.Servicio).all()
    busqueda_res = motor.buscar_lugares(q, servicios)
    
    return [{
        "datos": {
            "id_servicio": r["servicio"].id,
            "nombre_servicio": r["servicio"].nombre,
            "piso": r["servicio"].piso,
            "nombre_edificio": r["servicio"].edificio.nombre,
            "lat": r["servicio"].edificio.lat,
            "lng": r["servicio"].edificio.lng,
            "popularidad": r["servicio"].popularidad,
            "keywords": r["servicio"].keywords
        },
        "score": float(r["score"]),
        "motivo": r["motivo"]
    } for r in busqueda_res]

@app.get("/recomendaciones/{email}", response_model=List[models.RecomendacionResponse])
def get_recomendaciones(email: str, db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user: 
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    motor = ml_engine.MotorRecomendacion()
    servicios = db.query(models.Servicio).all()
    recoms = motor.recomendar_servicios(user.pref_comida, user.pref_estudio, user.pref_hobby, servicios)
    
    return [{
        "datos": {
            "id_servicio": r["servicio"].id,
            "nombre_servicio": r["servicio"].nombre,
            "piso": r["servicio"].piso,
            "nombre_edificio": r["servicio"].edificio.nombre,
            "lat": r["servicio"].edificio.lat,
            "lng": r["servicio"].edificio.lng,
            "popularidad": r["servicio"].popularidad
        },
        "score": r["score"],
        "motivo": r["motivo"]
    } for r in recoms]

@app.get("/edificios", response_model=List[models.EdificioBasico])
def get_edificios(db: Session = Depends(database.get_db)):
    eds = db.query(models.Edificio).all()
    return [{
        "id": e.id,
        "nombre": e.nombre,
        "lat": e.lat,
        "lng": e.lng,
        "descripcion": e.descripcion or "Edificio EPN",
        "servicios": [s.nombre for s in e.servicios]
    } for e in eds]