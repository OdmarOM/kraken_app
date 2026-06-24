from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AvisoEventoCreate(BaseModel):
    titulo: str
    contenido: str
    imagen_url: Optional[str] = None
    tipo: str = "aviso"
    audiencia: str = "publico"
    activo: bool = True
    fecha_evento: Optional[str] = None
    creado_por: Optional[str] = None


class AvisoEventoUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    imagen_url: Optional[str] = None
    tipo: Optional[str] = None
    audiencia: Optional[str] = None
    activo: Optional[bool] = None
    fecha_evento: Optional[str] = None


class AvisoEventoResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
    imagen_url: Optional[str] = None
    tipo: str
    audiencia: str
    activo: bool
    fecha_publicacion: datetime
    fecha_evento: Optional[datetime] = None
    creado_por: Optional[str] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
