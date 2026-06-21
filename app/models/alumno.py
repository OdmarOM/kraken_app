from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class NivelGorra(str, enum.Enum):
    BLANCA = "Blanca"
    AMARILLA = "Amarilla"
    ROJA = "Roja"
    AZUL = "Azul"
    PLATEADA = "Plateada"
    DORADA = "Dorada"
    NEGRA = "Negra"
    ADULTOS = "Adultos"


class Alumno(Base):
    __tablename__ = "alumnos"

    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutores.id", ondelete="CASCADE"), nullable=False, index=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="SET NULL"), nullable=True, index=True)
    nombre = Column(String(100), nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    edad = Column(Integer, nullable=True)
    nivel_gorra = Column(SQLEnum(NivelGorra), nullable=False, default=NivelGorra.BLANCA)
    fecha_corte_pago = Column(Date, nullable=True)  # Fecha límite de pago mensual
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    tutor = relationship("Tutor", back_populates="alumnos")
    grupo = relationship("Grupo", back_populates="alumnos", uselist=False)
    asistencias = relationship("Asistencia", back_populates="alumno", cascade="all, delete-orphan")
    evaluaciones = relationship("Evaluacion", back_populates="alumno", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="alumno", cascade="all, delete-orphan")
