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
    
    # Features para IA
    es_lugar_comida = Column(Boolean, default=False)
    es_lugar_estudio = Column(Boolean, default=False)
    es_lugar_hobby = Column(Boolean, default=False)
    
    # RELACIONES
    eventos = relationship("EventoDB", back_populates="edificio", cascade="all, delete-orphan")
    # Nueva relación: Servicios
    servicios_lista = relationship("ServicioDB", back_populates="edificio", cascade="all, delete-orphan")

class ServicioDB(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String) # Ej: "Baños", "Ascensor", "Fotocopiadora"
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    
    edificio = relationship("EdificioDB", back_populates="servicios_lista")

class EventoDB(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    tipo_evento = Column(String)
    
    edificio = relationship("EdificioDB", back_populates="eventos")