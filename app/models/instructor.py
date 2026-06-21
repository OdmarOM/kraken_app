from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Instructor(Base):
    __tablename__ = "instructores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), unique=True, nullable=False, index=True)
    whatsapp_numero = Column(String(20), unique=True, nullable=True, index=True)
    email = Column(String(100), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con Grupos
    grupos = relationship("Grupo", back_populates="instructor", cascade="all, delete-orphan")
