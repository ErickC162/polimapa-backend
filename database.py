from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://polimapa_db_user:9J6uATleShh1UrZVM9v1uN25kRhZ4FN4@dpg-d5j63infte5s73d6oab0-a/polimapa_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()