from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.tutor import Tutor
from app.models.instructor import Instructor
from app.models.lead import Lead

router = APIRouter(prefix="/busqueda", tags=["busqueda"])


@router.get("/telefono/{telefono}")
def buscar_por_telefono(telefono: str, db: Session = Depends(get_db)):
    """Busca un número de teléfono en tutores, instructores y leads (prospectos)"""
    
    # Buscar en tutores
    tutor = db.query(Tutor).filter(Tutor.telefono == telefono).first()
    if tutor:
        return {
            "tipo": "tutor",
            "encontrado": True,
            "datos": {
                "id": tutor.id,
                "nombre": tutor.nombre,
                "telefono": tutor.telefono,
                "email": tutor.email,
                "activo": tutor.activo
            }
        }
    
    # Buscar en instructores
    instructor = db.query(Instructor).filter(Instructor.telefono == telefono).first()
    if instructor:
        return {
            "tipo": "instructor",
            "encontrado": True,
            "datos": {
                "id": instructor.id,
                "nombre": instructor.nombre,
                "telefono": instructor.telefono,
                "email": instructor.email,
                "activo": instructor.activo
            }
        }
    
    # Buscar en leads (prospectos)
    lead = db.query(Lead).filter(Lead.telefono == telefono).first()
    if lead:
        return {
            "tipo": "prospecto",
            "encontrado": True,
            "datos": {
                "id": lead.id,
                "nombre": lead.nombre,
                "telefono": lead.telefono,
                "interes": lead.interes,
                "estatus": lead.estatus,
                "notas": lead.notas
            }
        }
    
    # No encontrado en ninguna tabla
    return {
        "tipo": None,
        "encontrado": False,
        "mensaje": "No se encontró el número de teléfono en tutores, instructores ni prospectos"
    }
