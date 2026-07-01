from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    telefono = Column(String(20), primary_key=True, index=True)
    nombre_usuario = Column(String(100), nullable=True)
    datos_conversacionales = Column(String, nullable=True)
    ultima_interaccion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
