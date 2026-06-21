from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
from app.models.alumno import NivelGorra


class ObjetivoSemanal(Base):
    __tablename__ = "objetivos_semanales"

    id = Column(Integer, primary_key=True, index=True)
    nivel_gorra = Column(SQLEnum(NivelGorra), nullable=False, index=True)
    semana = Column(Integer, nullable=False)  # Número de semana (1-52)
    año = Column(Integer, nullable=False, index=True)
    descripcion = Column(String(500), nullable=False)
    activo = Column(Integer, default=1)  # 1 = activo, 0 = inactivo
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
