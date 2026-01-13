from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- 1. MODELOS DE DATOS (Lo que llega desde Android) ---

class PreferenciasUsuario(BaseModel):
    # Recibimos los índices tal cual están en tu EncuestaActivity.kt
    sel_comida: int   # 0: Almuerzo, 1: Rápida, 2: Saludable, 3: Cafetería
    sel_estudio: int  # 0: Biblioteca, 1: Grupal, 2: AireLibre...
    sel_hobby: int    # 0: Fútbol, 1: Básquet, 2: Ecuavóley, 3: Gaming...

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str  # ESTE ES EL ID ÚNICO
    preferencias: PreferenciasUsuario

class Edificio(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    etiquetas: List[str] # Ej: ["comida_rapida", "wifi", "gaming"]
    descripcion: str

class Evento(BaseModel):
    nombre: str
    edificio_id: int
    etiqueta_relacionada: str # Con qué preferencia hace match este evento

# --- 2. MAPEO DE ÍNDICES (Traductor Kotlin -> Python) ---
# Esto debe coincidir con el orden de tus listas en Kotlin
MAPA_COMIDA = {0: "almuerzo_economico", 1: "comida_rapida", 2: "comida_saludable", 3: "cafeteria"}
MAPA_ESTUDIO = {0: "biblioteca_silencio", 1: "estudio_grupal", 2: "aire_libre", 3: "laboratorio_pc", 4: "aulas_vacias"}
MAPA_HOBBY = {0: "futbol", 1: "basquet", 2: "ecuavoley", 3: "gaming", 4: "gym", 5: "relax"}

# --- 3. BASE DE DATOS SIMULADA ---

db_usuarios = [] # Lista de diccionarios

# Edificios con etiquetas que coinciden con los mapas de arriba
db_edificios = [
    Edificio(id=1, nombre="Comedor Central", lat=-0.2100, lng=-78.4900, 
             etiquetas=["almuerzo_economico"], descripcion="Almuerzos completos a buen precio."),
    Edificio(id=2, nombre="Pizzería Politécnica", lat=-0.2105, lng=-78.4905, 
             etiquetas=["comida_rapida", "estudio_grupal"], descripcion="Pizza y mesas grandes."),
    Edificio(id=3, nombre="Biblioteca Central", lat=-0.2110, lng=-78.4910, 
             etiquetas=["biblioteca_silencio", "relax"], descripcion="Silencio absoluto."),
    Edificio(id=4, nombre="Asociación de Sistemas", lat=-0.2120, lng=-78.4920, 
             etiquetas=["gaming", "laboratorio_pc"], descripcion="Área de juegos y cómputo."),
    Edificio(id=5, nombre="Canchas Principales", lat=-0.2130, lng=-78.4930, 
             etiquetas=["futbol", "aire_libre"], descripcion="Canchas de césped sintético."),
]

# Eventos activos hoy
db_eventos = [
    Evento(nombre="Torneo FC26", edificio_id=4, etiqueta_relacionada="gaming"),
    Evento(nombre="Feria de Nutrición", edificio_id=1, etiqueta_relacionada="comida_saludable")
]

# --- 4. LÓGICA DE RECOMENDACIÓN (Random Forest Simulado) ---

def calcular_puntaje(usuario: UsuarioRegistro, edificio: Edificio):
    score = 0
    prefs = usuario.preferencias
    
    # Traducir los índices del usuario a etiquetas de texto
    mis_gustos = [
        MAPA_COMIDA.get(prefs.sel_comida),
        MAPA_ESTUDIO.get(prefs.sel_estudio),
        MAPA_HOBBY.get(prefs.sel_hobby)
    ]
    
    # A. Coincidencia de Preferencias (Peso: 20 pts cada match)
    for gusto in mis_gustos:
        if gusto in edificio.etiquetas:
            score += 20
            
    # B. Coincidencia de Eventos (Peso: 50 pts!! Importa mucho)
    evento_aqui = next((e for e in db_eventos if e.edificio_id == edificio.id), None)
    if evento_aqui:
        score += 30 # Puntos solo por haber evento
        # Si el evento es DE LO QUE ME GUSTA -> Super Boost
        if evento_aqui.etiqueta_relacionada in mis_gustos:
            score += 50 

    return score, evento_aqui

# --- 5. ENDPOINTS ---

@app.post("/registrar")
def registrar_usuario(datos: UsuarioRegistro):
    # Verificar si el correo ya existe
    if any(u.email == datos.email for u in db_usuarios):
        # Si existe, actualizamos sus preferencias (opcional)
        for i, u in enumerate(db_usuarios):
            if u.email == datos.email:
                db_usuarios[i] = datos
        return {"mensaje": "Preferencias actualizadas", "usuario": datos.nombre}
    
    # Si no existe, lo creamos
    db_usuarios.append(datos)
    return {"mensaje": "Usuario registrado con éxito", "usuario": datos.nombre}

@app.get("/recomendaciones/{email}")
def obtener_recomendaciones(email: str):
    # 1. Buscar usuario por EMAIL
    usuario = next((u for u in db_usuarios if u.email == email), None)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado. Regístrate primero.")

    # 2. Evaluar cada edificio
    resultados = []
    for ed in db_edificios:
        puntaje, evento = calcular_puntaje(usuario, ed)
        
        motivo = "Recomendado por tus gustos"
        if evento:
            motivo = f"¡Evento hoy!: {evento.nombre}"
        
        if puntaje > 0: # Solo agregar si tiene algún sentido ir
            resultados.append({
                "edificio": ed,
                "score": puntaje,
                "motivo": motivo
            })
            
    # 3. Ordenar y devolver Top 3
    resultados = sorted(resultados, key=lambda x: x["score"], reverse=True)[:3]
    return resultados