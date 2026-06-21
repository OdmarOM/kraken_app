from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from app.models.alumno import NivelGorra


class AlumnoBase(BaseModel):
    tutor_id: int
    grupo_id: Optional[int] = None
    nombre: str
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = None
    nivel_gorra: NivelGorra = NivelGorra.BLANCA
    fecha_corte_pago: Optional[date] = None
    activo: bool = True


class AlumnoCreate(AlumnoBase):
    pass


class AlumnoUpdate(BaseModel):
    grupo_id: Optional[int] = None
    nombre: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = None
    nivel_gorra: Optional[NivelGorra] = None
    fecha_corte_pago: Optional[date] = None
    activo: Optional[bool] = None


class AlumnoResponse(AlumnoBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
