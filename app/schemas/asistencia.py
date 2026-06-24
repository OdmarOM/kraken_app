from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class AsistenciaBase(BaseModel):
    alumno_id: int
    grupo_id: Optional[int] = None
    instructor_id: Optional[int] = None
    fecha: date
    presente: bool = True
    observaciones: Optional[str] = None


class AsistenciaCreate(AsistenciaBase):
    pass


class AsistenciaUpdate(BaseModel):
    presente: Optional[bool] = None
    observaciones: Optional[str] = None


class AsistenciaResponse(BaseModel):
    id: int
    alumno_id: int
    grupo_id: Optional[int] = None
    instructor_id: Optional[int] = None
    fecha: date
    presente: bool
    observaciones: Optional[str] = None
    nombre_grupo: Optional[str] = None
    nivel_gorra: Optional[str] = None
    nombre_instructor: Optional[str] = None
    nombre_alumno: Optional[str] = None
    registrado_por: Optional[str] = None
    creado_en: datetime

    class Config:
        from_attributes = True


class AsistenciaConDetalles(AsistenciaResponse):
    nombre_alumno_actual: Optional[str] = None
    nombre_grupo_actual: Optional[str] = None
    nombre_instructor_actual: Optional[str] = None


class TomarAsistenciaRequest(BaseModel):
    grupo_id: int
    instructor_id: int
    fecha: date
    asistencias: list[dict]  # [{alumno_id: 1, presente: true, observaciones: "..."}]
