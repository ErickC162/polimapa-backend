from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    pref_comida = Column(Integer)
    pref_estudio = Column(Integer)
    pref_hobby = Column(Integer)

class EdificioDB(Base):
    __tablename__ = "edificios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    descripcion = Column(String)
    
    # Variables ("Features") para el algoritmo Random Forest
    es_lugar_comida = Column(Boolean, default=False)
    es_lugar_estudio = Column(Boolean, default=False)
    es_lugar_hobby = Column(Boolean, default=False)
    
    # Relación con eventos
    eventos = relationship("EventoDB", back_populates="edificio")

class EventoDB(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    tipo_evento = Column(String) # "comida", "estudio", "hobby"
    
    edificio = relationship("EdificioDB", back_populates="eventos")