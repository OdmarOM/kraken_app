from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from calendar import month_name

from app.database import get_db
from app.models.pago import Pago, EstatusPago
from app.models.alumno import Alumno
from app.schemas.pago import PagoCreate, PagoUpdate, PagoResponse, PagoConAlumno

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.get("/", response_model=List[PagoConAlumno])
def get_pagos(
    skip: int = 0,
    limit: int = 100,
    estatus: Optional[EstatusPago] = None,
    mes: Optional[int] = None,
    anio: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Pago).join(Alumno)
    
    if estatus:
        query = query.filter(Pago.estatus == estatus)
    if mes:
        query = query.filter(Pago.mes == mes)
    if anio:
        query = query.filter(Pago.anio == anio)
    
    pagos = query.order_by(Pago.anio.desc(), Pago.mes.desc()).offset(skip).limit(limit).all()
    
    result = []
    for pago in pagos:
        result.append({
            **pago.__dict__,
            'alumno_nombre': pago.alumno.nombre,
            'tutor_nombre': pago.alumno.tutor.nombre,
            'tutor_telefono': pago.alumno.tutor.telefono,
            'tutor_email': pago.alumno.tutor.email
        })
    
    return result


@router.get("/alumno/{alumno_id}", response_model=List[PagoResponse])
def get_pagos_por_alumno(alumno_id: int, db: Session = Depends(get_db)):
    pagos = db.query(Pago).filter(Pago.alumno_id == alumno_id).order_by(Pago.anio.desc(), Pago.mes.desc()).all()
    return pagos


@router.get("/{pago_id}", response_model=PagoConAlumno)
def get_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    return {
        **pago.__dict__,
        'alumno_nombre': pago.alumno.nombre,
        'tutor_nombre': pago.alumno.tutor.nombre,
        'tutor_telefono': pago.alumno.tutor.telefono,
        'tutor_email': pago.alumno.tutor.email
    }


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def create_pago(pago: PagoCreate, db: Session = Depends(get_db)):
    alumno = db.query(Alumno).filter(Alumno.id == pago.alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Verificar si ya existe pago para este alumno en este mes/año
    pago_existente = db.query(Pago).filter(
        Pago.alumno_id == pago.alumno_id,
        Pago.mes == pago.mes,
        Pago.anio == pago.anio
    ).first()
    
    if pago_existente:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un pago para este alumno en este mes"
        )
    
    db_pago = Pago(**pago.model_dump())
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago


@router.put("/{pago_id}", response_model=PagoResponse)
def update_pago(pago_id: int, pago: PagoUpdate, db: Session = Depends(get_db)):
    db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    update_data = pago.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_pago, key, value)
    
    db.commit()
    db.refresh(db_pago)
    return db_pago


@router.delete("/{pago_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pago(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(Pago).filter(Pago.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    
    db.delete(db_pago)
    db.commit()
    return None


@router.post("/generar-mensuales", response_model=List[PagoResponse])
def generar_pagos_mensuales(mes: int, anio: int, monto: float, db: Session = Depends(get_db)):
    """Genera pagos para todos los alumnos activos para un mes específico"""
    # Obtener alumnos activos
    alumnos_activos = db.query(Alumno).filter(Alumno.activo == True).all()
    
    pagos_creados = []
    for alumno in alumnos_activos:
        # Verificar si ya existe pago
        pago_existente = db.query(Pago).filter(
            Pago.alumno_id == alumno.id,
            Pago.mes == mes,
            Pago.anio == anio
        ).first()
        
        if not pago_existente:
            # Calcular fecha límite (día 5 del mes)
            fecha_limite = date(anio, mes, 5)
            
            nuevo_pago = Pago(
                alumno_id=alumno.id,
                mes_correspondiente=f"{month_name[mes]} {anio}",
                anio=anio,
                mes=mes,
                monto=monto,
                estatus=EstatusPago.PENDIENTE,
                fecha_limite=fecha_limite
            )
            db.add(nuevo_pago)
            pagos_creados.append(nuevo_pago)
    
    db.commit()
    
    for pago in pagos_creados:
        db.refresh(pago)
    
    return pagos_creados


@router.post("/actualizar-estatus-vencidos")
def actualizar_estatus_vencidos(db: Session = Depends(get_db)):
    """Actualiza el estatus de pagos pendientes a vencidos si pasó la fecha límite"""
    hoy = date.today()
    
    pagos_vencidos = db.query(Pago).filter(
        Pago.estatus == EstatusPago.PENDIENTE,
        Pago.fecha_limite < hoy
    ).all()
    
    for pago in pagos_vencidos:
        pago.estatus = EstatusPago.VENCIDO
    
    db.commit()
    
    return {"mensaje": f"Se actualizaron {len(pagos_vencidos)} pagos a vencido"}
