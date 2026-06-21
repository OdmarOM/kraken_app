from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class TutorBase(BaseModel):
    nombre: str
    telefono: str
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    activo: bool = True


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    direccion: Optional[str] = None
    notas: Optional[str] = None
    activo: Optional[bool] = None


class TutorResponse(TutorBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
