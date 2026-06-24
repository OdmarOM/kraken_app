from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import os

from app.database import get_db
from app.models.aviso_evento import AvisoEvento
from app.schemas.aviso_evento import (
    AvisoEventoCreate, AvisoEventoUpdate, AvisoEventoResponse
)

router = APIRouter(prefix="/avisos-eventos", tags=["avisos-eventos"])


@router.get("/", response_model=List[AvisoEventoResponse])
def get_avisos_eventos(
    activo: Optional[bool] = None,
    tipo: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene todos los avisos y eventos con filtros opcionales"""
    query = db.query(AvisoEvento)
    
    if activo is not None:
        query = query.filter(AvisoEvento.activo == activo)
    
    if tipo:
        query = query.filter(AvisoEvento.tipo == tipo)
    
    avisos = query.order_by(AvisoEvento.fecha_publicacion.desc()).offset(skip).limit(limit).all()
    return avisos


@router.get("/{aviso_id}", response_model=AvisoEventoResponse)
def get_aviso_evento(aviso_id: int, db: Session = Depends(get_db)):
    """Obtiene un aviso/evento específico"""
    aviso = db.query(AvisoEvento).filter(AvisoEvento.id == aviso_id).first()
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso/Evento no encontrado")
    return aviso


@router.post("/", response_model=AvisoEventoResponse, status_code=status.HTTP_201_CREATED)
def create_aviso_evento(aviso: AvisoEventoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo aviso o evento"""
    data = aviso.model_dump()
    print(f"Datos recibidos para crear aviso: {data}")
    
    # Convertir fecha_evento de string a datetime si existe
    if data.get('fecha_evento'):
        try:
            data['fecha_evento'] = datetime.strptime(data['fecha_evento'], '%Y-%m-%d')
        except (ValueError, TypeError):
            data['fecha_evento'] = None
    else:
        data['fecha_evento'] = None
    
    nuevo_aviso = AvisoEvento(**data)
    db.add(nuevo_aviso)
    db.commit()
    db.refresh(nuevo_aviso)
    print(f"Aviso creado con imagen_url: {nuevo_aviso.imagen_url}")
    return nuevo_aviso


@router.put("/{aviso_id}", response_model=AvisoEventoResponse)
def update_aviso_evento(
    aviso_id: int,
    aviso: AvisoEventoUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza un aviso/evento"""
    db_aviso = db.query(AvisoEvento).filter(AvisoEvento.id == aviso_id).first()
    if not db_aviso:
        raise HTTPException(status_code=404, detail="Aviso/Evento no encontrado")
    
    update_data = aviso.model_dump(exclude_unset=True)
    print(f"Datos de actualización: {update_data}")
    print(f"Imagen actual en DB: {db_aviso.imagen_url}")
    
    # Si se está actualizando la imagen, eliminar la anterior
    if 'imagen_url' in update_data and update_data['imagen_url'] != db_aviso.imagen_url:
        if db_aviso.imagen_url:
            try:
                if db_aviso.imagen_url.startswith('/uploads/eventos/'):
                    filename = db_aviso.imagen_url.split('/')[-1]
                    file_path = Path("/opt/acuaticapp-backend/uploads/eventos") / filename
                    
                    if file_path.exists():
                        os.remove(file_path)
                        print(f"Imagen anterior eliminada: {filename}")
            except Exception as e:
                print(f"Error al eliminar imagen anterior: {e}")
    
    # Convertir fecha_evento de string a datetime si existe
    if 'fecha_evento' in update_data and update_data['fecha_evento']:
        try:
            update_data['fecha_evento'] = datetime.strptime(update_data['fecha_evento'], '%Y-%m-%d')
        except (ValueError, TypeError):
            update_data['fecha_evento'] = None
    elif 'fecha_evento' in update_data and not update_data['fecha_evento']:
        update_data['fecha_evento'] = None
    
    for key, value in update_data.items():
        setattr(db_aviso, key, value)
    
    db.commit()
    db.refresh(db_aviso)
    return db_aviso


@router.delete("/{aviso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aviso_evento(aviso_id: int, db: Session = Depends(get_db)):
    """Elimina un aviso/evento"""
    db_aviso = db.query(AvisoEvento).filter(AvisoEvento.id == aviso_id).first()
    if not db_aviso:
        raise HTTPException(status_code=404, detail="Aviso/Evento no encontrado")
    
    # Eliminar la imagen asociada si existe
    if db_aviso.imagen_url:
        try:
            if db_aviso.imagen_url.startswith('/uploads/eventos/'):
                filename = db_aviso.imagen_url.split('/')[-1]
                file_path = Path("/opt/acuaticapp-backend/uploads/eventos") / filename
                
                if file_path.exists():
                    os.remove(file_path)
                    print(f"Imagen de evento eliminada: {filename}")
        except Exception as e:
            print(f"Error al eliminar imagen: {e}")
    
    db.delete(db_aviso)
    db.commit()
    return None
