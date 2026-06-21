from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.lead import EstatusLead, InteresLead

class LeadBase(BaseModel):
    nombre: str
    telefono: str
    interes: InteresLead
    estatus: EstatusLead = EstatusLead.PENDIENTE
    notas: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    interes: Optional[InteresLead] = None
    estatus: Optional[EstatusLead] = None
    notas: Optional[str] = None
    ultimo_seguimiento: Optional[datetime] = None

class LeadResponse(LeadBase):
    id: int
    fecha_captura: datetime
    ultimo_seguimiento: Optional[datetime] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True
