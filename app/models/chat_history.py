from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String(20), index=True)
    rol = Column(String(20))
    contenido = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
