from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tutor(Base):
    __tablename__ = "tutores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), unique=True, nullable=False, index=True)  # WhatsApp como llave principal
    email = Column(String(100), nullable=True)
    direccion = Column(String(200), nullable=True)
    notas = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación 1:N con Alumnos
    alumnos = relationship("Alumno", back_populates="tutor", cascade="all, delete-orphan")
