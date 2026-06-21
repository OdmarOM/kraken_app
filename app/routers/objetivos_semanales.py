from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.objetivo_semanal import ObjetivoSemanal
from app.schemas.objetivo_semanal import ObjetivoSemanalCreate, ObjetivoSemanalUpdate, ObjetivoSemanalResponse

router = APIRouter(prefix="/objetivos-semanales", tags=["objetivos-semanales"])

@router.get("/", response_model=List[ObjetivoSemanalResponse])
def get_objetivos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    objetivos = db.query(ObjetivoSemanal).filter(ObjetivoSemanal.activo == 1).order_by(
        ObjetivoSemanal.año.desc(),
        ObjetivoSemanal.semana.desc()
    ).offset(skip).limit(limit).all()
    return objetivos

@router.get("/{objetivo_id}", response_model=ObjetivoSemanalResponse)
def get_objetivo(objetivo_id: int, db: Session = Depends(get_db)):
    objetivo = db.query(ObjetivoSemanal).filter(ObjetivoSemanal.id == objetivo_id).first()
    if not objetivo:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    return objetivo

@router.get("/nivel/{nivel_gorra}", response_model=List[ObjetivoSemanalResponse])
def get_objetivos_por_nivel(nivel_gorra: str, db: Session = Depends(get_db)):
    objetivos = db.query(ObjetivoSemanal).filter(
        ObjetivoSemanal.nivel_gorra == nivel_gorra,
        ObjetivoSemanal.activo == 1
    ).order_by(
        ObjetivoSemanal.año.desc(),
        ObjetivoSemanal.semana.desc()
    ).all()
    return objetivos

@router.post("/", response_model=ObjetivoSemanalResponse, status_code=status.HTTP_201_CREATED)
def create_objetivo(objetivo: ObjetivoSemanalCreate, db: Session = Depends(get_db)):
    # Validar que la semana esté entre 1 y 52
    if objetivo.semana < 1 or objetivo.semana > 52:
        raise HTTPException(
            status_code=400,
            detail="La semana debe estar entre 1 y 52"
        )
    
    # Validar que el año sea razonable
    current_year = datetime.now().year
    if objetivo.año < current_year - 1 or objetivo.año > current_year + 1:
        raise HTTPException(
            status_code=400,
            detail=f"El año debe estar entre {current_year - 1} y {current_year + 1}"
        )
    
    db_objetivo = ObjetivoSemanal(**objetivo.model_dump())
    db.add(db_objetivo)
    db.commit()
    db.refresh(db_objetivo)
    return db_objetivo

@router.put("/{objetivo_id}", response_model=ObjetivoSemanalResponse)
def update_objetivo(objetivo_id: int, objetivo: ObjetivoSemanalUpdate, db: Session = Depends(get_db)):
    db_objetivo = db.query(ObjetivoSemanal).filter(ObjetivoSemanal.id == objetivo_id).first()
    if not db_objetivo:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    
    update_data = objetivo.model_dump(exclude_unset=True)
    
    # Validaciones si se actualizan semana o año
    if 'semana' in update_data:
        if update_data['semana'] < 1 or update_data['semana'] > 52:
            raise HTTPException(
                status_code=400,
                detail="La semana debe estar entre 1 y 52"
            )
    
    if 'año' in update_data:
        current_year = datetime.now().year
        if update_data['año'] < current_year - 1 or update_data['año'] > current_year + 1:
            raise HTTPException(
                status_code=400,
                detail=f"El año debe estar entre {current_year - 1} y {current_year + 1}"
            )
    
    for key, value in update_data.items():
        setattr(db_objetivo, key, value)
    
    db.commit()
    db.refresh(db_objetivo)
    return db_objetivo

@router.delete("/{objetivo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_objetivo(objetivo_id: int, db: Session = Depends(get_db)):
    db_objetivo = db.query(ObjetivoSemanal).filter(ObjetivoSemanal.id == objetivo_id).first()
    if not db_objetivo:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    
    # Soft delete
    db_objetivo.activo = 0
    db.commit()
    return None
