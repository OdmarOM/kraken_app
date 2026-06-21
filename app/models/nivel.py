from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class Nivel(Base):
    __tablename__ = "niveles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)  # amarilla, roja, azul, plateada, dorada, negra, adultos
    color = Column(String(20), nullable=False)  # código de color hex o nombre
    activo = Column(Boolean, default=True)
