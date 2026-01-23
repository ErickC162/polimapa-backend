from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, ml_engine
from typing import List

app = FastAPI()

@app.get("/recomendaciones/{email}", response_model=List[models.RecomendacionResponse])
def get_recomendaciones(email: str, db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user: raise HTTPException(404, "Usuario no encontrado")
    
    motor = ml_engine.MotorRecomendacion()
    servicios = db.query(models.Servicio).all()
    predicciones = motor.recomendar_servicios(user.pref_comida, user.pref_estudio, user.pref_hobby, servicios)
    
    return [{
        "datos": {
            "id_servicio": p["servicio"].id,
            "nombre_servicio": p["servicio"].nombre,
            "piso": p["servicio"].piso,
            "nombre_edificio": p["servicio"].edificio.nombre,
            "lat": p["servicio"].edificio.lat,
            "lng": p["servicio"].edificio.lng,
            "popularidad": p["servicio"].popularidad
        },
        "score": p["score"],
        "motivo": p["motivo"]
    } for p in predicciones]