from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

# Importaciones locales
from database import engine, get_db
import models
from ml_engine import MotorRecomendacion

# Crear tablas (si no existen)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PoliMapa Backend V5 - Categorías", version="5.0")
recomendador = MotorRecomendacion()

# --- DICCIONARIOS PARA RESPUESTA ---
LABELS_COMIDA  = {0: "", 1: "Almuerzo", 2: "Comida Rápida", 3: "Saludable", 4: "Café"}
LABELS_ESTUDIO = {0: "", 1: "Biblioteca", 2: "Grupal", 3: "Aire Libre", 4: "Laboratorio", 5: "Aulas"}
LABELS_HOBBY   = {0: "", 1: "Fútbol", 2: "Básquet", 3: "Ecuavóley", 4: "Gaming", 5: "Gym", 6: "Relax"}

# --- SCHEMAS ---

class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

class ServicioData(BaseModel):
    id_servicio: int
    nombre_servicio: str
    piso: str
    nombre_edificio: str
    lat: float
    lng: float
    popularidad: int
    score: float
    categoria_match: str  # Ej: "Comida (Almuerzo)"
    motivo: str           # Ej: "Alta coincidencia en tus gustos"

class RecomendacionResponse(BaseModel):
    datos: ServicioData

# --- ENDPOINTS ---

@app.post("/usuarios/")
def crear_usuario(user: UsuarioRegistro, db: Session = Depends(get_db)):
    db_user = models.UsuarioDB(
        nombre=user.nombre, 
        email=user.email,
        pref_comida=user.preferencias.sel_comida,
        pref_estudio=user.preferencias.sel_estudio,
        pref_hobby=user.preferencias.sel_hobby
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "mensaje": "Usuario creado"}

@app.get("/recomendaciones/{usuario_id}", response_model=List[RecomendacionResponse])
def obtener_recomendaciones(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Traemos todos los servicios con su edificio
    servicios = db.query(models.ServicioDB).join(models.EdificioDB).all()
    
    ranking = []
    
    for s in servicios:
        # Filtro básico: Si el lugar no tiene NINGUNA capacidad (listas vacías), lo saltamos
        if not (s.lista_comida or s.lista_estudio or s.lista_hobby):
            continue

        # Usamos el motor ML para predecir
        score = recomendador.predecir(usuario, s)
        
        # Si el score es muy bajo, no lo recomendamos
        if score < 15:
            continue
            
        # Determinar etiqueta de visualización
        cat_match = "General"
        detalles = []
        
        # Lógica para mostrar qué hizo match
        # Verificamos si lo que el usuario quiere está en lo que el lugar ofrece
        if usuario.pref_comida in s.lista_comida:
            detalles.append(f"Comida: {LABELS_COMIDA.get(usuario.pref_comida)}")
        elif s.lista_comida: # Si ofrece comida pero no match exacto
             detalles.append("Comida")

        if usuario.pref_estudio in s.lista_estudio:
            detalles.append(f"Estudio: {LABELS_ESTUDIO.get(usuario.pref_estudio)}")
        elif s.lista_estudio:
            detalles.append("Estudio")
            
        if usuario.pref_hobby in s.lista_hobby:
            detalles.append(f"Hobby: {LABELS_HOBBY.get(usuario.pref_hobby)}")
        elif s.lista_hobby:
             detalles.append("Recreación")

        cat_str = " / ".join(detalles) if detalles else "Lugar de interés"

        ranking.append({
            "datos": {
                "id_servicio": s.id,
                "nombre_servicio": s.nombre,
                "piso": s.piso or "PB",
                "nombre_edificio": s.edificio.nombre,
                "lat": s.edificio.lat,
                "lng": s.edificio.lng,
                "popularidad": s.popularidad,
                "score": round(score, 2),
                "categoria_match": cat_str,
                "motivo": f"Popularidad: {s.popularidad}/10"
            }
        })

    # Ordenar por score descendente
    ranking.sort(key=lambda x: x["datos"]["score"], reverse=True)
    
    return ranking[:5]