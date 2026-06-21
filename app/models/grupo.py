from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.alumno import NivelGorra


class Grupo(Base):
    __tablename__ = "grupos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)  # Ej: "Grupo Principiante 1"
    nivel_asociado = Column(SQLEnum(NivelGorra), nullable=False)
    instructor_id = Column(Integer, ForeignKey("instructores.id", ondelete="SET NULL"), nullable=True, index=True)
    cupo_maximo = Column(Integer, nullable=False, default=10)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    instructor = relationship("Instructor", back_populates="grupos")
    alumnos = relationship("Alumno", back_populates="grupo")
    horarios = relationship("HorarioGrupo", back_populates="grupo", cascade="all, delete-orphan")
