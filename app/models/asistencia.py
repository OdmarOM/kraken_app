from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    grupo_id = Column(Integer, ForeignKey("grupos.id", ondelete="SET NULL"), nullable=True, index=True)
    fecha = Column(Date, nullable=False, index=True)
    presente = Column(Boolean, default=True)
    observaciones = Column(String(300), nullable=True)
    registrado_por = Column(String(50), nullable=True)  # Nombre del instructor o sistema
    creado_en = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    alumno = relationship("Alumno", back_populates="asistencias")
