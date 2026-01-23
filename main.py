from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import database
import models
import ml_engine

app = FastAPI(title="PoliMapa API")

# Dependencia para la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a PoliMapa API - EPN"}

# 1. REGISTRO DE USUARIO
@app.post("/registrar", response_model=models.RespuestaRegistro)
def registrar_usuario(usuario: models.UsuarioRegistro, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    db_usuario = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_usuario:
        # Si existe, actualizamos sus preferencias
        db_usuario.sel_comida = usuario.preferencias.sel_comida
        db_usuario.sel_estudio = usuario.preferencias.sel_estudio
        db_usuario.sel_hobby = usuario.preferencias.sel_hobby
        db.commit()
        return {"mensaje": "Preferencias actualizadas correctamente"}
    
    # Si no existe, crear uno nuevo
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        email=usuario.email,
        sel_comida=usuario.preferencias.sel_comida,
        sel_estudio=usuario.preferencias.sel_estudio,
        sel_hobby=usuario.preferencias.sel_hobby
    )
    db.add(nuevo_usuario)
    db.commit()
    return {"mensaje": "Usuario registrado exitosamente"}

# 2. OBTENER RECOMENDACIONES (La causa del error 422)
@app.get("/recomendaciones/{email}", response_model=List[models.RecomendacionResponse])
def obtener_recomendaciones(email: str, db: Session = Depends(get_db)):
    # 1. Buscar el usuario
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Obtener todos los servicios de la DB
    servicios = db.query(models.Servicio).all()
    if not servicios:
        return []

    # 3. Pasar los datos al motor de ML
    # El motor debe recibir las selecciones del usuario (0, 1, 2...)
    predicciones = ml_engine.recomendar_servicios(
        usuario.sel_comida, 
        usuario.sel_estudio, 
        usuario.sel_hobby, 
        servicios
    )

    # 4. Formatear la respuesta EXACTAMENTE como la espera Android
    resultado = []
    for p in predicciones:
        s = p["servicio"]
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

# 3. OBTENER TODOS LOS EDIFICIOS (Pines Azules)
@app.get("/edificios", response_model=List[models.EdificioBasico])
def obtener_edificios(db: Session = Depends(get_db)):
    edificios = db.query(models.Edificio).all()
    resultado = []
    for e in edificios:
        # Extraer lista de nombres de servicios
        nombres_servicios = [s.nombre for s in e.servicios]
        resultado.append({
            "id": e.id,
            "nombre": e.nombre,
            "lat": e.latitud,
            "lng": e.longitud,
            "descripcion": e.descripcion or "Edificio de la EPN",
            "servicios": nombres_servicios
        })
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)