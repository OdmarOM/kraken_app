from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class EstatusLead(str, enum.Enum):
    PENDIENTE = "Pendiente"
    CONTACTADO = "Contactado"
    EN_PROCESO = "En Proceso"
    CONVERTIDO = "Convertido"
    NO_INTERESADO = "No Interesado"


class InteresLead(str, enum.Enum):
    CLASE_PRUEBA = "Clase de Prueba"
    INSCRIPCION = "Inscripción"
    INSCRIBIR = "Inscribir"
    CONSULTAR_HORARIOS = "Consultar Horarios"
    SOLICITAR_INFORMACION = "Solicitar Información"
    CONTACTAR_PROFESOR = "Contactar Profesor"
    OTRO = "Otro"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False, index=True)
    interes = Column(SQLEnum(InteresLead), nullable=False)
    estatus = Column(SQLEnum(EstatusLead), nullable=False, default=EstatusLead.PENDIENTE, index=True)
    notas = Column(String(500), nullable=True)
    fecha_captura = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Para detectar abandonados (>24h)
    ultimo_seguimiento = Column(DateTime(timezone=True), nullable=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now())
    actualizado_en = Column(DateTime(timezone=True), onupdate=func.now())
