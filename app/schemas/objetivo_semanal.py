from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.alumno import NivelGorra

class ObjetivoSemanalBase(BaseModel):
    nivel_gorra: NivelGorra
    semana: int
    año: int
    descripcion: str
    activo: int = 1

class ObjetivoSemanalCreate(ObjetivoSemanalBase):
    pass

class ObjetivoSemanalUpdate(BaseModel):
    nivel_gorra: Optional[NivelGorra] = None
    semana: Optional[int] = None
    año: Optional[int] = None
    descripcion: Optional[str] = None
    activo: Optional[int] = None

class ObjetivoSemanalResponse(ObjetivoSemanalBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
