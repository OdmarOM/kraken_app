from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class InstructorBase(BaseModel):
    nombre: str
    telefono: str
    whatsapp_numero: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: bool = True


class InstructorCreate(InstructorBase):
    pass


class InstructorUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    whatsapp_numero: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None


class InstructorResponse(InstructorBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
