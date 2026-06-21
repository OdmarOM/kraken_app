from pydantic import BaseModel
from typing import Optional
from datetime import time
from app.models.horario_grupo import DiaSemana

class HorarioGrupoBase(BaseModel):
    dia_semana: DiaSemana
    hora_inicio: str  # formato "HH:MM"
    hora_fin: str    # formato "HH:MM"

class HorarioGrupoCreate(HorarioGrupoBase):
    grupo_id: Optional[int] = None  # Opcional porque se puede crear desde el grupo

class HorarioGrupoUpdate(BaseModel):
    dia_semana: Optional[DiaSemana] = None
    hora_inicio: Optional[str] = None
    hora_fin: Optional[str] = None

class HorarioGrupoResponse(BaseModel):
    id: int
    grupo_id: int
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fin: time

    class Config:
        from_attributes = True
