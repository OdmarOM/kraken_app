from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models.pago import EstatusPago


class PagoBase(BaseModel):
    alumno_id: int
    mes_correspondiente: str
    anio: int
    mes: int
    monto: float
    fecha_limite: date


class PagoCreate(PagoBase):
    pass


class PagoUpdate(BaseModel):
    estatus: Optional[str] = None
    fecha_pago: Optional[date] = None
    comprobante_url: Optional[str] = None
    aprobado_por: Optional[str] = None
    observaciones: Optional[str] = None


class PagoResponse(PagoBase):
    id: int
    estatus: EstatusPago
    fecha_pago: Optional[date] = None
    comprobante_url: Optional[str] = None
    aprobado_por: Optional[str] = None
    observaciones: Optional[str] = None
    creado_en: datetime
    actualizado_en: Optional[datetime] = None

    class Config:
        from_attributes = True


class PagoConAlumno(PagoResponse):
    alumno_nombre: str
    tutor_nombre: str
    tutor_telefono: str
    tutor_email: Optional[str] = None
