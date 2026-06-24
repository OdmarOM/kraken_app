from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime, time

from app.database import get_db
from app.models.asistencia import Asistencia
from app.models.alumno import Alumno
from app.models.grupo import Grupo
from app.models.instructor import Instructor
from app.models.horario_grupo import HorarioGrupo, DiaSemana
from app.schemas.asistencia import (
    AsistenciaCreate, AsistenciaUpdate, AsistenciaResponse, 
    AsistenciaConDetalles, TomarAsistenciaRequest
)

router = APIRouter(prefix="/asistencias", tags=["asistencias"])


@router.get("/grupos-en-clase")
def get_grupos_en_clase(db: Session = Depends(get_db)):
    """Obtiene los grupos que tienen clase en este momento con su % de asistencia de hoy"""
    # Obtener día y hora actual en GMT-6 (México)
    from datetime import timedelta
    ahora = datetime.utcnow() - timedelta(hours=6)
    dia_actual = ahora.strftime("%A")
    
    # Mapear día en inglés a enum
    dia_map = {
        "Monday": DiaSemana.LUNES,
        "Tuesday": DiaSemana.MARTES,
        "Wednesday": DiaSemana.MIERCOLES,
        "Thursday": DiaSemana.JUEVES,
        "Friday": DiaSemana.VIERNES,
        "Saturday": DiaSemana.SABADO,
        "Sunday": DiaSemana.DOMINGO
    }
    
    dia_enum = dia_map.get(dia_actual)
    if not dia_enum:
        return []
    
    hora_actual = ahora.time()
    fecha_hoy = ahora.date()
    
    # Buscar grupos con horarios en este día y hora
    horarios = db.query(HorarioGrupo).filter(
        HorarioGrupo.dia_semana == dia_enum,
        HorarioGrupo.hora_inicio <= hora_actual,
        HorarioGrupo.hora_fin >= hora_actual
    ).all()
    
    grupos_en_clase = []
    
    for horario in horarios:
        grupo = horario.grupo
        if not grupo or not grupo.activo:
            continue
        
        # Contar alumnos activos en el grupo
        total_alumnos = db.query(func.count(Alumno.id)).filter(
            Alumno.grupo_id == grupo.id,
            Alumno.activo == True
        ).scalar() or 0
        
        # Contar asistencias presentes hoy
        presentes = db.query(func.count(Asistencia.id)).filter(
            Asistencia.grupo_id == grupo.id,
            Asistencia.fecha == fecha_hoy,
            Asistencia.presente == True
        ).scalar() or 0
        
        porcentaje = (presentes / total_alumnos * 100) if total_alumnos > 0 else 0
        
        grupos_en_clase.append({
            "grupo_id": grupo.id,
            "nombre_grupo": grupo.nombre,
            "nivel_asociado": grupo.nivel_asociado.value,
            "instructor": grupo.instructor.nombre if grupo.instructor else "Sin asignar",
            "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
            "hora_fin": horario.hora_fin.strftime("%H:%M"),
            "total_alumnos": total_alumnos,
            "presentes": presentes,
            "porcentaje_asistencia": round(porcentaje, 1)
        })
    
    return grupos_en_clase


@router.post("/tomar", response_model=List[AsistenciaResponse])
def tomar_asistencia(request: TomarAsistenciaRequest, db: Session = Depends(get_db)):
    """Toma asistencia masiva para un grupo en una fecha específica"""
    # Verificar que el grupo existe
    grupo = db.query(Grupo).filter(Grupo.id == request.grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    # Verificar que el instructor existe
    instructor = db.query(Instructor).filter(Instructor.id == request.instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    asistencias_creadas = []
    
    for item in request.asistencias:
        # Verificar que el alumno existe
        alumno = db.query(Alumno).filter(Alumno.id == item['alumno_id']).first()
        if not alumno:
            continue
        
        # Verificar si ya existe asistencia para este alumno en esta fecha
        asistencia_existente = db.query(Asistencia).filter(
            Asistencia.alumno_id == item['alumno_id'],
            Asistencia.fecha == request.fecha
        ).first()
        
        if asistencia_existente:
            # Actualizar si ya existe
            asistencia_existente.presente = item.get('presente', True)
            asistencia_existente.observaciones = item.get('observaciones')
            asistencia_existente.instructor_id = request.instructor_id
            asistencia_existente.registrado_por = instructor.nombre
            asistencias_creadas.append(asistencia_existente)
        else:
            # Crear nueva asistencia con campos estáticos
            nueva_asistencia = Asistencia(
                alumno_id=item['alumno_id'],
                grupo_id=request.grupo_id,
                instructor_id=request.instructor_id,
                fecha=request.fecha,
                presente=item.get('presente', True),
                observaciones=item.get('observaciones'),
                nombre_grupo=grupo.nombre,
                nivel_gorra=alumno.nivel_gorra,
                nombre_instructor=instructor.nombre,
                nombre_alumno=alumno.nombre,
                registrado_por=instructor.nombre
            )
            db.add(nueva_asistencia)
            asistencias_creadas.append(nueva_asistencia)
    
    db.commit()
    
    for asistencia in asistencias_creadas:
        db.refresh(asistencia)
    
    return asistencias_creadas


@router.get("/alumno/{alumno_id}", response_model=List[AsistenciaConDetalles])
def get_asistencias_por_alumno(
    alumno_id: int, 
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene el historial de asistencias de un alumno"""
    asistencias = db.query(Asistencia).filter(
        Asistencia.alumno_id == alumno_id
    ).order_by(Asistencia.fecha.desc()).offset(skip).limit(limit).all()
    
    result = []
    for asistencia in asistencias:
        result.append({
            **asistencia.__dict__,
            'nombre_alumno_actual': asistencia.alumno.nombre if asistencia.alumno else None,
            'nombre_grupo_actual': asistencia.grupo.nombre if asistencia.grupo else None,
            'nombre_instructor_actual': asistencia.instructor.nombre if asistencia.instructor else None
        })
    
    return result


@router.get("/grupo/{grupo_id}/fecha/{fecha}", response_model=List[AsistenciaResponse])
def get_asistencias_por_grupo_fecha(
    grupo_id: int, 
    fecha: date,
    db: Session = Depends(get_db)
):
    """Obtiene las asistencias de un grupo en una fecha específica"""
    asistencias = db.query(Asistencia).filter(
        Asistencia.grupo_id == grupo_id,
        Asistencia.fecha == fecha
    ).all()
    
    return asistencias


@router.get("/instructor/{instructor_id}", response_model=List[AsistenciaResponse])
def get_asistencias_por_instructor(
    instructor_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene las asistencias registradas por un instructor"""
    asistencias = db.query(Asistencia).filter(
        Asistencia.instructor_id == instructor_id
    ).order_by(Asistencia.fecha.desc()).offset(skip).limit(limit).all()
    
    return asistencias


@router.get("/grupo/{grupo_id}/alumnos", response_model=List[dict])
def get_alumnos_grupo_para_asistencia(grupo_id: int, db: Session = Depends(get_db)):
    """Obtiene los alumnos de un grupo para tomar asistencia (endpoint para WhatsApp)"""
    alumnos = db.query(Alumno).filter(
        Alumno.grupo_id == grupo_id,
        Alumno.activo == True
    ).all()
    
    return [
        {
            "alumno_id": alumno.id,
            "nombre": alumno.nombre,
            "nivel_gorra": alumno.nivel_gorra
        }
        for alumno in alumnos
    ]


@router.get("/", response_model=List[AsistenciaResponse])
def get_asistencias(
    grupo_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene asistencias con filtros opcionales"""
    query = db.query(Asistencia)
    
    if grupo_id:
        query = query.filter(Asistencia.grupo_id == grupo_id)
    
    asistencias = query.order_by(Asistencia.fecha.desc()).offset(skip).limit(limit).all()
    return asistencias


@router.get("/{asistencia_id}", response_model=AsistenciaConDetalles)
def get_asistencia(asistencia_id: int, db: Session = Depends(get_db)):
    """Obtiene una asistencia específica"""
    asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    
    return {
        **asistencia.__dict__,
        'nombre_alumno_actual': asistencia.alumno.nombre if asistencia.alumno else None,
        'nombre_grupo_actual': asistencia.grupo.nombre if asistencia.grupo else None,
        'nombre_instructor_actual': asistencia.instructor.nombre if asistencia.instructor else None
    }


@router.put("/{asistencia_id}", response_model=AsistenciaResponse)
def update_asistencia(
    asistencia_id: int, 
    asistencia: AsistenciaUpdate, 
    db: Session = Depends(get_db)
):
    """Actualiza una asistencia"""
    db_asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    
    update_data = asistencia.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_asistencia, key, value)
    
    db.commit()
    db.refresh(db_asistencia)
    return db_asistencia


@router.delete("/{asistencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asistencia(asistencia_id: int, db: Session = Depends(get_db)):
    """Elimina una asistencia"""
    db_asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    
    db.delete(db_asistencia)
    db.commit()
    return None


@router.get("/grupo/{grupo_id}/alumnos", response_model=List[dict])
def get_alumnos_grupo_para_asistencia(grupo_id: int, db: Session = Depends(get_db)):
    """Obtiene los alumnos de un grupo para tomar asistencia (endpoint para WhatsApp)"""
    alumnos = db.query(Alumno).filter(
        Alumno.grupo_id == grupo_id,
        Alumno.activo == True
    ).all()
    
    return [
        {
            "alumno_id": alumno.id,
            "nombre": alumno.nombre,
            "nivel_gorra": alumno.nivel_gorra
        }
        for alumno in alumnos
    ]


@router.get("/grupos-en-clase")
def get_grupos_en_clase(db: Session = Depends(get_db)):
    """Obtiene los grupos que tienen clase en este momento con su % de asistencia de hoy"""
    # Obtener día y hora actual en GMT-6 (México)
    from datetime import timedelta
    ahora = datetime.utcnow() - timedelta(hours=6)
    dia_actual = ahora.strftime("%A")
    
    # Mapear día en inglés a enum
    dia_map = {
        "Monday": DiaSemana.LUNES,
        "Tuesday": DiaSemana.MARTES,
        "Wednesday": DiaSemana.MIERCOLES,
        "Thursday": DiaSemana.JUEVES,
        "Friday": DiaSemana.VIERNES,
        "Saturday": DiaSemana.SABADO,
        "Sunday": DiaSemana.DOMINGO
    }
    
    dia_enum = dia_map.get(dia_actual)
    if not dia_enum:
        return []
    
    hora_actual = ahora.time()
    fecha_hoy = ahora.date()
    
    # Buscar grupos con horarios en este día y hora
    horarios = db.query(HorarioGrupo).filter(
        HorarioGrupo.dia_semana == dia_enum,
        HorarioGrupo.hora_inicio <= hora_actual,
        HorarioGrupo.hora_fin >= hora_actual
    ).all()
    
    grupos_en_clase = []
    
    for horario in horarios:
        grupo = horario.grupo
        if not grupo or not grupo.activo:
            continue
        
        # Contar alumnos activos en el grupo
        total_alumnos = db.query(func.count(Alumno.id)).filter(
            Alumno.grupo_id == grupo.id,
            Alumno.activo == True
        ).scalar() or 0
        
        # Contar asistencias presentes hoy
        presentes = db.query(func.count(Asistencia.id)).filter(
            Asistencia.grupo_id == grupo.id,
            Asistencia.fecha == fecha_hoy,
            Asistencia.presente == True
        ).scalar() or 0
        
        porcentaje = (presentes / total_alumnos * 100) if total_alumnos > 0 else 0
        
        grupos_en_clase.append({
            "grupo_id": grupo.id,
            "nombre_grupo": grupo.nombre,
            "nivel_asociado": grupo.nivel_asociado.value,
            "instructor": grupo.instructor.nombre if grupo.instructor else "Sin asignar",
            "hora_inicio": horario.hora_inicio.strftime("%H:%M"),
            "hora_fin": horario.hora_fin.strftime("%H:%M"),
            "total_alumnos": total_alumnos,
            "presentes": presentes,
            "porcentaje_asistencia": round(porcentaje, 1)
        })
    
    return grupos_en_clase
