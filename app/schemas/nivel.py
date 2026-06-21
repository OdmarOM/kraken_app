from pydantic import BaseModel
from typing import Optional

class NivelBase(BaseModel):
    nombre: str
    color: str
    activo: bool = True

class NivelCreate(NivelBase):
    pass

class NivelUpdate(BaseModel):
    nombre: Optional[str] = None
    color: Optional[str] = None
    activo: Optional[bool] = None

class NivelResponse(NivelBase):
    id: int

    class Config:
        from_attributes = True
