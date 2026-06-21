from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Evaluacion(Base):
    __tablename__ = "evaluaciones"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, index=True)
    tecnica = Column(Integer, nullable=False)  # Escala 1-10
    resistencia = Column(Integer, nullable=False)  # Escala 1-10
    coordinacion = Column(Integer, nullable=False)  # Escala 1-10
    actitud = Column(Integer, nullable=False)  # Escala 1-10
    promedio = Column(Integer, nullable=False)  # Promedio de las 4 métricas
    observaciones = Column(String(500), nullable=True)
    evaluado_por = Column(String(50), nullable=True)  # Nombre del instructor
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    presentado_al_tutor = Column(Boolean, default=False, nullable=False)  # Si se debe presentar al tutor
    fecha_entrega_tutor = Column(DateTime(timezone=True), nullable=True)  # Cuándo se le presentó al tutor

    # Relaciones
    alumno = relationship("Alumno", back_populates="evaluaciones")
