from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class AdminBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    nombre_completo: str
    telefono: Optional[str] = None
    activo: bool = True


class AdminCreate(AdminBase):
    password: str


class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None


class AdminResponse(AdminBase):
    id: int
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
