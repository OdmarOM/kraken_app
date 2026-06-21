from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
import bcrypt
from jose import JWTError, jwt

from app.database import get_db
from app.models.admin import Admin
from app.models.alumno import Alumno
from app.models.grupo import Grupo
from app.models.instructor import Instructor
from app.models.tutor import Tutor
from app.models.pago import Pago, EstatusPago
from app.models.lead import Lead, EstatusLead
from app.schemas.admin import Token
from app.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin is None:
        raise credentials_exception
    return admin


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not admin.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def read_users_me(current_admin: Admin = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "username": current_admin.username,
        "email": current_admin.email,
        "nombre_completo": current_admin.nombre_completo,
        "activo": current_admin.activo
    }


@router.get("/estadisticas")
def get_estadisticas(db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)):
    """Obtiene estadísticas generales del sistema"""
    
    # Contar alumnos por nivel
    alumnos_por_nivel = db.query(
        Alumno.nivel_gorra,
        func.count(Alumno.id).label('cantidad')
    ).filter(Alumno.activo == True).group_by(Alumno.nivel_gorra).all()
    
    # Contar alumnos por grupo
    alumnos_por_grupo = db.query(
        Grupo.nombre,
        func.count(Alumno.id).label('cantidad')
    ).join(Alumno, Alumno.grupo_id == Grupo.id).filter(
        Alumno.activo == True,
        Grupo.activo == True
    ).group_by(Grupo.nombre).all()
    
    # Calcular cupos disponibles por grupo
    grupos_con_cupo = []
    grupos = db.query(Grupo).filter(Grupo.activo == True).all()
    for grupo in grupos:
        alumnos_en_grupo = db.query(Alumno).filter(
            Alumno.grupo_id == grupo.id,
            Alumno.activo == True
        ).count()
        cupo_disponible = grupo.cupo_maximo - alumnos_en_grupo
        grupos_con_cupo.append({
            "grupo_id": grupo.id,
            "nombre": grupo.nombre,
            "cupo_maximo": grupo.cupo_maximo,
            "alumnos_actuales": alumnos_en_grupo,
            "cupo_disponible": cupo_disponible,
            "porcentaje_ocupado": round((alumnos_en_grupo / grupo.cupo_maximo) * 100, 1) if grupo.cupo_maximo > 0 else 0
        })
    
    # Distribución por edad
    hoy = date.today()
    edad_ranges = {
        "3-5": 0,
        "6-8": 0,
        "9-12": 0,
        "13-15": 0,
        "16+": 0
    }
    
    alumnos = db.query(Alumno).filter(Alumno.activo == True).all()
    for alumno in alumnos:
        if alumno.edad:
            if alumno.edad <= 5:
                edad_ranges["3-5"] += 1
            elif alumno.edad <= 8:
                edad_ranges["6-8"] += 1
            elif alumno.edad <= 12:
                edad_ranges["9-12"] += 1
            elif alumno.edad <= 15:
                edad_ranges["13-15"] += 1
            else:
                edad_ranges["16+"] += 1
    
    # Estadísticas de cobranza del mes actual
    hoy = date.today()
    mes_actual = hoy.month
    anio_actual = hoy.year
    
    pagos_mes = db.query(Pago).filter(
        Pago.mes == mes_actual,
        Pago.anio == anio_actual
    ).all()
    
    pagos_pendientes = db.query(Pago).filter(Pago.estatus == EstatusPago.PENDIENTE).count()
    pagos_vencidos = db.query(Pago).filter(Pago.estatus == EstatusPago.VENCIDO).count()
    pagos_pagados = db.query(Pago).filter(Pago.estatus == EstatusPago.PAGADO).count()
    pagos_en_revision = db.query(Pago).filter(Pago.estatus == EstatusPago.EN_REVISION).count()
    
    total_recaudado = sum([pago.monto for pago in pagos_mes if pago.estatus == EstatusPago.PAGADO])
    total_pendiente = sum([pago.monto for pago in pagos_mes if pago.estatus in [EstatusPago.PENDIENTE, EstatusPago.VENCIDO]])
    
    # Estadísticas de leads
    leads_por_estatus = db.query(
        Lead.estatus,
        func.count(Lead.id).label('cantidad')
    ).group_by(Lead.estatus).all()
    
    leads_nuevos_mes = db.query(Lead).filter(
        func.extract('month', Lead.creado_en) == mes_actual,
        func.extract('year', Lead.creado_en) == anio_actual
    ).count()
    
    return {
        "totales": {
            "alumnos": db.query(Alumno).filter(Alumno.activo == True).count(),
            "grupos": db.query(Grupo).filter(Grupo.activo == True).count(),
            "instructores": db.query(Instructor).filter(Instructor.activo == True).count(),
            "tutores": db.query(Tutor).filter(Tutor.activo == True).count()
        },
        "alumnos_por_nivel": [{"nivel": nivel, "cantidad": cantidad} for nivel, cantidad in alumnos_por_nivel],
        "alumnos_por_grupo": [{"grupo": grupo, "cantidad": cantidad} for grupo, cantidad in alumnos_por_grupo],
        "grupos_con_cupo": grupos_con_cupo,
        "distribucion_edad": edad_ranges,
        "cobranza": {
            "pendientes": pagos_pendientes,
            "vencidos": pagos_vencidos,
            "pagados": pagos_pagados,
            "en_revision": pagos_en_revision,
            "total_recaudado": float(total_recaudado),
            "total_pendiente": float(total_pendiente)
        },
        "leads": {
            "por_estatus": [{"estatus": estatus, "cantidad": cantidad} for estatus, cantidad in leads_por_estatus],
            "nuevos_mes": leads_nuevos_mes
        }
    }
