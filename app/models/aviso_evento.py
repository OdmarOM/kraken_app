from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AvisoEvento(Base):
    __tablename__ = "avisos_eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    contenido = Column(Text, nullable=False)
    imagen_url = Column(String(500), nullable=True)
    tipo = Column(String(50), nullable=False, default="aviso")  # "aviso" o "evento"
    audiencia = Column(String(50), nullable=False, default="publico")  # "publico" o "miembros"
    activo = Column(Boolean, default=True)
    fecha_publicacion = Column(DateTime(timezone=True), server_default=func.now())
    fecha_evento = Column(DateTime(timezone=True), nullable=True)  # Para eventos con fecha específica
    creado_por = Column(String(100), nullable=True)  # Nombre del usuario que creó el aviso
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
