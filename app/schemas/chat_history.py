from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatHistoryBase(BaseModel):
    telefono: str
    rol: str
    contenido: str


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistoryResponse(ChatHistoryBase):
    id: int
    telefono: str
    rol: str
    contenido: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True
