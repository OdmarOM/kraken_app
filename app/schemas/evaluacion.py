from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class EvaluacionBase(BaseModel):
    alumno_id: int
    fecha: date
    tecnica: int
    resistencia: int
    coordinacion: int
    actitud: int
    observaciones: Optional[str] = None
    evaluado_por: Optional[str] = None
    presentado_al_tutor: Optional[bool] = False

class EvaluacionCreate(EvaluacionBase):
    pass

class EvaluacionUpdate(BaseModel):
    fecha: Optional[date] = None
    tecnica: Optional[int] = None
    resistencia: Optional[int] = None
    coordinacion: Optional[int] = None
    actitud: Optional[int] = None
    observaciones: Optional[str] = None
    evaluado_por: Optional[str] = None
    presentado_al_tutor: Optional[bool] = None
    fecha_entrega_tutor: Optional[datetime] = None

class EvaluacionResponse(EvaluacionBase):
    id: int
    promedio: int
    creado_en: datetime
    fecha_entrega_tutor: Optional[datetime] = None

    class Config:
        from_attributes = True
