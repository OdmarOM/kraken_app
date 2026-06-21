from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class EstatusPago(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"  # Cuando se envía comprobante vía WhatsApp
    PAGADO = "PAGADO"
    VENCIDO = "VENCIDO"


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False, index=True)
    mes_correspondiente = Column(String(20), nullable=False)  # Ej: "Enero 2024"
    anio = Column(Integer, nullable=False)  # Ej: 2024
    mes = Column(Integer, nullable=False)  # Ej: 1 para Enero
    monto = Column(Numeric(10, 2), nullable=False)
    estatus = Column(SQLEnum(EstatusPago), nullable=False, default=EstatusPago.PENDIENTE)
    fecha_pago = Column(Date, nullable=True)
    fecha_limite = Column(Date, nullable=False)  # Día 5 del mes
    comprobante_url = Column(String(500), nullable=True)  # URL de la imagen enviada por WhatsApp
    aprobado_por = Column(String(50), nullable=True)  # Admin que aprobó el pago
    observaciones = Column(String(300), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    alumno = relationship("Alumno", back_populates="pagos")
