from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import database
import models
import ml_engine

app = FastAPI(title="PoliMapa API")

# Dependencia de DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"mensaje": "PoliMapa API Funcionando"}

@app.post("/registrar", response_model=models.RespuestaRegistro)
def registrar_usuario(usuario: models.UsuarioRegistro, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    
    if db_usuario:
        db_usuario.nombre = usuario.nombre
        db_usuario.sel_comida = usuario.preferencias.sel_comida
        db_usuario.sel_estudio = usuario.preferencias.sel_estudio
        db_usuario.sel_hobby = usuario.preferencias.sel_hobby
    else:
        nuevo_usuario = models.Usuario(
            nombre=usuario.nombre,
            email=usuario.email,
            sel_comida=usuario.preferencias.sel_comida,
            sel_estudio=usuario.preferencias.sel_estudio,
            sel_hobby=usuario.preferencias.sel_hobby
        )
        db.add(nuevo_usuario)
    
    db.commit()
    return models.RespuestaRegistro(mensaje="Usuario procesado correctamente")

@app.get("/recomendaciones/{email}", response_model=List[models.RecomendacionResponse])
def obtener_recomendaciones(email: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    servicios = db.query(models.Servicio).all()
    # ml_engine procesa y devuelve lista de diccionarios {'servicio', 'score', 'motivo'}
    predicciones = ml_engine.recomendar_servicios(
        usuario.sel_comida, 
        usuario.sel_estudio, 
        usuario.sel_hobby, 
        servicios
    )

    resultado = []
    for p in predicciones:
        s = p["servicio"]
        # Mapeo manual para transformar latitud/longitud de DB a lat/lng de API
        resultado.append({
            "datos": {
                "id_servicio": s.id,
                "nombre_servicio": s.nombre,
                "piso": s.piso,
                "nombre_edificio": s.edificio.nombre,
                "lat": s.edificio.latitud,
                "lng": s.edificio.longitud,
                "categoria": s.categoria,
                "popularidad": s.popularidad,
                "caps_comida_str": s.caps_comida_str,
                "caps_estudio_str": s.caps_estudio_str,
                "caps_hobby_str": s.caps_hobby_str
            },
            "score": float(p["score"]),
            "motivo": p["motivo"]
        })
    return resultado

@app.get("/edificios", response_model=List[models.EdificioBasico])
def obtener_edificios(db: Session = Depends(get_db)):
    edificios = db.query(models.Edificio).all()
    return [
        {
            "id": e.id,
            "nombre": e.nombre,
            "lat": e.latitud,
            "lng": e.longitud,
            "descripcion": e.descripcion or "Sin descripción",
            "servicios": [s.nombre for s in e.servicios]
        } for e in edificios
    ]