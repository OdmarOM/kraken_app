from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import time

from app.database import get_db
from app.models.grupo import Grupo
from app.models.horario_grupo import HorarioGrupo, DiaSemana
from app.models.instructor import Instructor
from app.schemas.grupo import GrupoCreate, GrupoUpdate, GrupoResponse
from app.schemas.horario_grupo import HorarioGrupoCreate

router = APIRouter(prefix="/grupos", tags=["grupos"])


def validar_horario(hora_inicio: str, hora_fin: str) -> bool:
    """Valida que la hora de inicio sea anterior a la hora de fin"""
    if hora_inicio >= hora_fin:
        raise HTTPException(
            status_code=400,
            detail="La hora de inicio debe ser anterior a la hora de fin"
        )
    return True


def validar_conflicto_instructor(instructor_id: int, dia_semana: str, hora_inicio: str, hora_fin: str, db: Session, grupo_id: int = None) -> bool:
    """Valida que el instructor no tenga conflictos de horario"""
    if not instructor_id:
        return True
    
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    # Buscar horarios de grupos del mismo instructor en el mismo día
    from sqlalchemy import and_
    horarios_conflicto = db.query(HorarioGrupo).join(Grupo).filter(
        Grupo.instructor_id == instructor_id,
        HorarioGrupo.dia_semana == dia_semana,
        Grupo.activo == True
    )
    
    # Excluir el grupo actual si estamos actualizando
    if grupo_id:
        horarios_conflicto = horarios_conflicto.filter(HorarioGrupo.grupo_id != grupo_id)
    
    horarios_conflicto = horarios_conflicto.all()
    
    for horario in horarios_conflicto:
        # Verificar si hay superposición de horarios
        if (hora_inicio < horario.hora_fin and hora_fin > horario.hora_inicio):
            raise HTTPException(
                status_code=400,
                detail=f"El instructor tiene conflicto de horario con otro grupo el {dia_semana} ({horario.hora_inicio} - {horario.hora_fin})"
            )
    
    return True


@router.post("/", response_model=GrupoResponse, status_code=status.HTTP_201_CREATED)
def create_grupo(grupo: GrupoCreate, db: Session = Depends(get_db)):
    # Validar instructor si se asigna uno
    if grupo.instructor_id:
        instructor = db.query(Instructor).filter(Instructor.id == grupo.instructor_id).first()
        if not instructor:
            raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    # Validar cupo mínimo
    if grupo.cupo_maximo < 1:
        raise HTTPException(
            status_code=400,
            detail="El cupo máximo debe ser al menos 1"
        )
    
    # Validar horarios
    if not grupo.horarios:
        raise HTTPException(
            status_code=400,
            detail="El grupo debe tener al menos un horario"
        )
    
    for horario_data in grupo.horarios:
        validar_horario(horario_data['hora_inicio'], horario_data['hora_fin'])
        
        # Validar conflicto de instructor
        if grupo.instructor_id:
            validar_conflicto_instructor(
                grupo.instructor_id,
                horario_data['dia_semana'],
                horario_data['hora_inicio'],
                horario_data['hora_fin'],
                db
            )
    
    # Crear grupo sin horarios primero
    grupo_data = grupo.model_dump(exclude={'horarios'})
    db_grupo = Grupo(**grupo_data)
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    
    # Crear horarios
    for horario_data in grupo.horarios:
        horario = HorarioGrupo(
            grupo_id=db_grupo.id,
            dia_semana=horario_data['dia_semana'],
            hora_inicio=horario_data['hora_inicio'],
            hora_fin=horario_data['hora_fin']
        )
        db.add(horario)
    
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


@router.get("/", response_model=List[GrupoResponse])
def get_grupos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    grupos = db.query(Grupo).filter(Grupo.activo == True).offset(skip).limit(limit).all()
    return grupos


@router.get("/{grupo_id}", response_model=GrupoResponse)
def get_grupo(grupo_id: int, db: Session = Depends(get_db)):
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return grupo


@router.put("/{grupo_id}", response_model=GrupoResponse)
def update_grupo(grupo_id: int, grupo: GrupoUpdate, db: Session = Depends(get_db)):
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not db_grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    update_data = grupo.model_dump(exclude_unset=True, exclude={'horarios'})
    
    # Validar cupo mínimo si se cambia
    if 'cupo_maximo' in update_data and update_data['cupo_maximo'] < 1:
        raise HTTPException(
            status_code=400,
            detail="El cupo máximo debe ser al menos 1"
        )
    
    # Validar que no se reduzca el cupo por debajo de los alumnos actuales
    if 'cupo_maximo' in update_data:
        from app.models.alumno import Alumno
        alumnos_actuales = db.query(Alumno).filter(
            Alumno.grupo_id == grupo_id, 
            Alumno.activo == True
        ).count()
        
        if update_data['cupo_maximo'] < alumnos_actuales:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede reducir el cupo por debajo de los alumnos actuales ({alumnos_actuales})"
            )
    
    # Actualizar campos del grupo
    for key, value in update_data.items():
        setattr(db_grupo, key, value)
    
    # Actualizar horarios si se proporcionan
    if grupo.horarios is not None:
        # Eliminar horarios existentes
        db.query(HorarioGrupo).filter(HorarioGrupo.grupo_id == grupo_id).delete()
        
        # Validar y crear nuevos horarios
        for horario_data in grupo.horarios:
            validar_horario(horario_data['hora_inicio'], horario_data['hora_fin'])
            
            # Validar conflicto de instructor
            instructor_id = update_data.get('instructor_id', db_grupo.instructor_id)
            if instructor_id:
                validar_conflicto_instructor(
                    instructor_id,
                    horario_data['dia_semana'],
                    horario_data['hora_inicio'],
                    horario_data['hora_fin'],
                    db,
                    grupo_id
                )
            
            horario = HorarioGrupo(
                grupo_id=grupo_id,
                dia_semana=horario_data['dia_semana'],
                hora_inicio=horario_data['hora_inicio'],
                hora_fin=horario_data['hora_fin']
            )
            db.add(horario)
    
    db.commit()
    db.refresh(db_grupo)
    return db_grupo


@router.delete("/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_grupo(grupo_id: int, db: Session = Depends(get_db)):
    db_grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not db_grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Soft delete
    db_grupo.activo = False
    db.commit()
    return None
