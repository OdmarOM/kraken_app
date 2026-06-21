from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.database import get_db
from app.models.alumno import Alumno
from app.models.grupo import Grupo
from app.schemas.alumno import AlumnoCreate, AlumnoUpdate, AlumnoResponse

router = APIRouter(prefix="/alumnos", tags=["alumnos"])


def calcular_edad(fecha_nacimiento: date) -> int:
    """Calcula la edad basada en la fecha de nacimiento"""
    if not fecha_nacimiento:
        return None
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
    return edad


def validar_cupo_grupo(grupo_id: int, db: Session) -> bool:
    """Valida si hay cupo disponible en el grupo"""
    if not grupo_id:
        return True
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    alumnos_en_grupo = db.query(Alumno).filter(Alumno.grupo_id == grupo_id, Alumno.activo == True).count()
    
    if alumnos_en_grupo >= grupo.cupo_maximo:
        raise HTTPException(
            status_code=400, 
            detail=f"El grupo {grupo.nombre} no tiene cupo disponible. Cupo máximo: {grupo.cupo_maximo}"
        )
    
    return True


@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
def create_alumno(alumno: AlumnoCreate, db: Session = Depends(get_db)):
    # Validar que el tutor existe
    from app.models.tutor import Tutor
    tutor = db.query(Tutor).filter(Tutor.id == alumno.tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor no encontrado")
    
    # Validar cupo del grupo si se asigna uno
    if alumno.grupo_id:
        validar_cupo_grupo(alumno.grupo_id, db)
        
        # Validar que el nivel del alumno coincida con el nivel del grupo
        grupo = db.query(Grupo).filter(Grupo.id == alumno.grupo_id).first()
        if grupo and alumno.nivel_gorra != grupo.nivel_asociado:
            raise HTTPException(
                status_code=400,
                detail=f"El nivel del alumno ({alumno.nivel_gorra}) no coincide con el nivel del grupo ({grupo.nivel_asociado})"
            )
    
    # Calcular edad automáticamente si se proporciona fecha de nacimiento
    edad = calcular_edad(alumno.fecha_nacimiento)
    
    db_alumno = Alumno(**alumno.model_dump())
    if edad:
        db_alumno.edad = edad
    db.add(db_alumno)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno


@router.get("/", response_model=List[AlumnoResponse])
def get_alumnos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    alumnos = db.query(Alumno).offset(skip).limit(limit).all()
    return alumnos


@router.get("/{alumno_id}", response_model=AlumnoResponse)
def get_alumno(alumno_id: int, db: Session = Depends(get_db)):
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno


@router.put("/{alumno_id}", response_model=AlumnoResponse)
def update_alumno(alumno_id: int, alumno: AlumnoUpdate, db: Session = Depends(get_db)):
    db_alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    update_data = alumno.model_dump(exclude_unset=True)
    
    # Validar cupo si se cambia de grupo
    if 'grupo_id' in update_data and update_data['grupo_id'] != db_alumno.grupo_id:
        validar_cupo_grupo(update_data['grupo_id'], db)
        
        # Validar nivel del grupo
        if update_data['grupo_id']:
            grupo = db.query(Grupo).filter(Grupo.id == update_data['grupo_id']).first()
            nivel_alumno = update_data.get('nivel_gorra', db_alumno.nivel_gorra)
            if grupo and nivel_alumno != grupo.nivel_asociado:
                raise HTTPException(
                    status_code=400,
                    detail=f"El nivel del alumno ({nivel_alumno}) no coincide con el nivel del grupo ({grupo.nivel_asociado})"
                )
    
    # Recalcular edad si se cambia la fecha de nacimiento
    if 'fecha_nacimiento' in update_data:
        update_data['edad'] = calcular_edad(update_data['fecha_nacimiento'])
    
    for key, value in update_data.items():
        setattr(db_alumno, key, value)
    
    db.commit()
    db.refresh(db_alumno)
    return db_alumno


@router.delete("/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alumno(alumno_id: int, db: Session = Depends(get_db)):
    db_alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    db.delete(db_alumno)
    db.commit()
    return None
