from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class FAQBase(BaseModel):
    pregunta: str
    respuesta: str
    categoria: Optional[str] = None
    activo: bool = True
    orden: int = 0


class FAQCreate(FAQBase):
    pass


class FAQUpdate(BaseModel):
    pregunta: Optional[str] = None
    respuesta: Optional[str] = None
    categoria: Optional[str] = None
    activo: Optional[bool] = None
    orden: Optional[int] = None


class FAQResponse(FAQBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
