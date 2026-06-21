from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database import get_db
from app.models.evaluacion import Evaluacion
from app.schemas.evaluacion import EvaluacionCreate, EvaluacionUpdate, EvaluacionResponse

router = APIRouter(prefix="/evaluaciones", tags=["evaluaciones"])

@router.get("/", response_model=List[EvaluacionResponse])
def get_evaluaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    evaluaciones = db.query(Evaluacion).order_by(Evaluacion.fecha.desc()).offset(skip).limit(limit).all()
    return evaluaciones

@router.get("/alumno/{alumno_id}", response_model=List[EvaluacionResponse])
def get_evaluaciones_por_alumno(alumno_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    evaluaciones = db.query(Evaluacion).filter(
        Evaluacion.alumno_id == alumno_id
    ).order_by(Evaluacion.fecha.desc()).offset(skip).limit(limit).all()
    return evaluaciones

@router.get("/{evaluacion_id}", response_model=EvaluacionResponse)
def get_evaluacion(evaluacion_id: int, db: Session = Depends(get_db)):
    evaluacion = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()
    if not evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    return evaluacion

@router.post("/", response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED)
def create_evaluacion(evaluacion: EvaluacionCreate, db: Session = Depends(get_db)):
    # Validar que las calificaciones estén entre 1 y 10
    for campo in ['tecnica', 'resistencia', 'coordinacion', 'actitud']:
        valor = getattr(evaluacion, campo)
        if valor < 1 or valor > 10:
            raise HTTPException(
                status_code=400,
                detail=f"El campo {campo} debe estar entre 1 y 10"
            )
    
    # Calcular promedio
    promedio = (evaluacion.tecnica + evaluacion.resistencia + evaluacion.coordinacion + evaluacion.actitud) // 4
    
    db_evaluacion = Evaluacion(**evaluacion.model_dump())
    db_evaluacion.promedio = promedio
    db.add(db_evaluacion)
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion

@router.put("/{evaluacion_id}", response_model=EvaluacionResponse)
def update_evaluacion(evaluacion_id: int, evaluacion: EvaluacionUpdate, db: Session = Depends(get_db)):
    db_evaluacion = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()
    if not db_evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")
    
    update_data = evaluacion.model_dump(exclude_unset=True)
    
    # Validar calificaciones si se actualizan
    for campo in ['tecnica', 'resistencia', 'coordinacion', 'actitud']:
        if campo in update_data:
            valor = update_data[campo]
            if valor < 1 or valor > 10:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo {campo} debe estar entre 1 y 10"
                )
    
    # Recalcular promedio si se actualizan calificaciones
    campos_calificacion = ['tecnica', 'resistencia', 'coordinacion', 'actitud']
    if any(campo in update_data for campo in campos_calificacion):
        tecnica = update_data.get('tecnica', db_evaluacion.tecnica)
        resistencia = update_data.get('resistencia', db_evaluacion.resistencia)
        coordinacion = update_data.get('coordinacion', db_evaluacion.coordinacion)
        actitud = update_data.get('actitud', db_evaluacion.actitud)
        update_data['promedio'] = (tecnica + resistencia + coordinacion + actitud) // 4
    
    for key, value in update_data.items():
        setattr(db_evaluacion, key, value)
    
    db.commit()
    db.refresh(db_evaluacion)
    return db_evaluacion

@router.delete("/{evaluacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evaluacion(evaluacion_id: int, db: Session = Depends(get_db)):
    db_evaluacion = db.query(Evaluacion).filter(Evaluacion.id == evaluacion_id).first()
    if not db_evaluacion:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    db.delete(db_evaluacion)
    db.commit()
    return None
