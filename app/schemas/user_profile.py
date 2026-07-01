from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserProfileBase(BaseModel):
    telefono: str
    nombre_usuario: Optional[str] = None
    datos_conversacionales: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    nombre_usuario: Optional[str] = None
    datos_conversacionales: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    telefono: str
    nombre_usuario: Optional[str] = None
    datos_conversacionales: Optional[str] = None
    ultima_interaccion: Optional[datetime] = None

    class Config:
        from_attributes = True
