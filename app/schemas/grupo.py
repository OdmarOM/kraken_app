from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.alumno import NivelGorra
from app.schemas.horario_grupo import HorarioGrupoResponse


class GrupoBase(BaseModel):
    nombre: str
    nivel_asociado: NivelGorra
    instructor_id: Optional[int] = None
    cupo_maximo: int = 10
    activo: bool = True


class GrupoCreate(GrupoBase):
    horarios: List[dict]  # Lista de horarios: [{"dia_semana": "Lunes", "hora_inicio": "14:00", "hora_fin": "16:00"}, ...]


class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    nivel_asociado: Optional[NivelGorra] = None
    instructor_id: Optional[int] = None
    cupo_maximo: Optional[int] = None
    activo: Optional[bool] = None
    horarios: Optional[List[dict]] = None


class GrupoResponse(GrupoBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None
    horarios: List[HorarioGrupoResponse] = []
    disponibilidad: Optional[int] = None  # Lugares disponibles (cupo_maximo - alumnos_actuales)

    class Config:
        from_attributes = True
