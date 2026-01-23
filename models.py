from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    email = Column(String, unique=True, index=True)
    # Preferencias del 0 al N según tus diccionarios
    pref_comida = Column(Integer, default=0)
    pref_estudio = Column(Integer, default=0)
    pref_hobby = Column(Integer, default=0)

class EdificioDB(Base):
    __tablename__ = "edificios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    descripcion = Column(String)
    
    servicios_lista = relationship("ServicioDB", back_populates="edificio", cascade="all, delete-orphan")

class ServicioDB(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    piso = Column(String)
    edificio_id = Column(Integer, ForeignKey("edificios.id"))
    
    # --- NUEVAS COLUMNAS REQUERIDAS ---
    popularidad = Column(Integer, default=5)
    
    # Almacenan ids separados por comas: "1,2,4"
    caps_comida_str = Column(String, default="")
    caps_estudio_str = Column(String, default="")
    caps_hobby_str = Column(String, default="")

    edificio = relationship("EdificioDB", back_populates="servicios_lista")

    # --- PROPIEDADES DE AYUDA (Helpers) ---
    # Estas propiedades convierten el texto de la BD en listas usables por Python
    @property
    def lista_comida(self):
        if not self.caps_comida_str: return []
        try:
            return [int(x) for x in self.caps_comida_str.split(',') if x.strip()]
        except ValueError:
            return []

    @property
    def lista_estudio(self):
        if not self.caps_estudio_str: return []
        try:
            return [int(x) for x in self.caps_estudio_str.split(',') if x.strip()]
        except ValueError:
            return []

    @property
    def lista_hobby(self):
        if not self.caps_hobby_str: return []
        try:
            return [int(x) for x in self.caps_hobby_str.split(',') if x.strip()]
        except ValueError:
            return []