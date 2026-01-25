from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, ml_engine
from typing import List

app = FastAPI()

@app.post("/registrar")
def registrar(usuario: models.UsuarioRegistro, db: Session = Depends(database.get_db)):
    db_u = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if not db_u:
        db_u = models.Usuario(email=usuario.email, nombre=usuario.nombre)
        db.add(db_u)
    db_u.pref_comida, db_u.pref_estudio, db_u.pref_hobby = usuario.preferencias.sel_comida, usuario.preferencias.sel_estudio, usuario.preferencias.sel_hobby
    db.commit()
    return {"mensaje": "Ok"}

@app.get("/buscar", response_model=List[models.ResultadoBusqueda])
def buscar(q: str, db: Session = Depends(database.get_db)):
    if not q: return []
    try:
        motor = ml_engine.MotorRecomendacion()
        # Carga ansiosa (joinedload) no es necesaria si lazy='joined' por defecto, 
        # pero es bueno asegurarse que 'edificio' esté cargado para los servicios.
        eds = db.query(models.Edificio).all()
        servs = db.query(models.Servicio).all()
        
        return motor.buscar_mixto(q, eds, servs)
    except Exception as e:
        print(f"Error en buscar: {e}") # Ver log del servidor
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recomendaciones/{email}", response_model=List[models.RecomendacionResponse])
def get_recomendaciones(email: str, db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not user: raise HTTPException(404, "No user")
    motor = ml_engine.MotorRecomendacion()
    servs = db.query(models.Servicio).all()
    recoms = motor.recomendar_servicios(user.pref_comida, user.pref_estudio, user.pref_hobby, servs)
    return [{"datos": {"id_servicio": r["servicio"].id, "nombre_servicio": r["servicio"].nombre, "piso": r["servicio"].piso, "nombre_edificio": r["servicio"].edificio.nombre, "lat": r["servicio"].edificio.lat, "lng": r["servicio"].edificio.lng, "popularidad": r["servicio"].popularidad}, "score": r["score"], "motivo": r["motivo"]} for r in recoms]

@app.get("/edificios", response_model=List[models.EdificioBasico])
def get_edificios(db: Session = Depends(database.get_db)):
    eds = db.query(models.Edificio).all()
    return [{"id": e.id, "nombre": e.nombre, "lat": e.lat, "lng": e.lng, "descripcion": e.descripcion or "", "servicios": [s.nombre for s in e.servicios]} for e in eds]