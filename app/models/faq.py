from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(String(500), nullable=False)
    respuesta = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=True)  # Para organizar por categorías
    activo = Column(Boolean, default=True)
    orden = Column(Integer, default=0)  # Para ordenar las FAQs
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
