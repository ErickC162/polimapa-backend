from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel
from typing import List, Optional

# --- MODELOS SQLALCHEMY ---
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    pref_comida = Column(Integer, default=0)
    pref_estudio = Column(Integer, default=0)
    pref_hobby = Column(Integer, default=0)

class Edificio(Base):
    __tablename__ = "edificios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    descripcion = Column(Text)
    keywords = Column(Text, default="") # Tags para búsqueda
    servicios = relationship("Servicio", back_populates="edificio")

class Servicio(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    piso = Column(String)
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    popularidad = Column(Integer, default=5)
    caps_comida_str = Column(String, default="")
    caps_estudio_str = Column(String, default="")
    caps_hobby_str = Column(String, default="")
    keywords = Column(Text, default="") # Tags para búsqueda
    
    edificio = relationship("Edificio", back_populates="servicios")

    @property
    def lista_comida(self): return [int(x) for x in self.caps_comida_str.split(',') if x.strip().isdigit()]
    @property
    def lista_estudio(self): return [int(x) for x in self.caps_estudio_str.split(',') if x.strip().isdigit()]
    @property
    def lista_hobby(self): return [int(x) for x in self.caps_hobby_str.split(',') if x.strip().isdigit()]

# --- ESQUEMAS PYDANTIC (API) ---
class EdificioBusqueda(BaseModel):
    id: int
    nombre: str
    lat: float
    lng: float
    score: float

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
    popularidad: int
    keywords: Optional[str] = ""

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