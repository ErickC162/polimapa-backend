from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import List, Optional

# ==========================================
# MODELOS DE BASE DE DATOS (SQLAlchemy)
# ==========================================

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    sel_comida = Column(Integer)
    sel_estudio = Column(Integer)
    sel_hobby = Column(Integer)

class Edificio(Base):
    __tablename__ = "edificios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)
    latitud = Column(Float)
    longitud = Column(Float)
    descripcion = Column(Text)
    servicios = relationship("Servicio", back_populates="edificio")

class Servicio(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    piso = Column(String)
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    categoria = Column(String)  # 'Comida', 'Estudio', 'Hobby'
    popularidad = Column(Integer, default=0)
    caps_comida_str = Column(String, nullable=True)
    caps_estudio_str = Column(String, nullable=True)
    caps_hobby_str = Column(String, nullable=True)
    
    edificio = relationship("Edificio", back_populates="servicios")

# ==========================================
# ESQUEMAS DE VALIDACIÓN (Pydantic)
# ==========================================

class PreferenciasInput(BaseModel):
    sel_comida: int
    sel_estudio: int
    sel_hobby: int

class UsuarioRegistro(BaseModel):
    nombre: str
    email: str
    preferencias: PreferenciasInput

class RespuestaRegistro(BaseModel):
    mensaje: str

class ServicioData(BaseModel):
    id_servicio: int
    nombre_servicio: str
    piso: str
    nombre_edificio: str
    lat: float
    lng: float
    categoria: str
    popularidad: Optional[int] = 0
    caps_comida_str: Optional[str] = None
    caps_estudio_str: Optional[str] = None
    caps_hobby_str: Optional[str] = None

    class Config:
        from_attributes = True

class RecomendacionResponse(BaseModel):
    datos: ServicioData
    score: float
    motivo: str

class EdificioBasico(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    descripcion: str
    servicios: List[str]