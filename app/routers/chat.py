from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.user_profile import UserProfile
from app.models.chat_history import ChatHistory
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from app.schemas.chat_history import ChatHistoryCreate, ChatHistoryResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/historial/{telefono}", response_model=List[ChatHistoryResponse])
def get_historial(telefono: str, limit: int = 15, db: Session = Depends(get_db)):
    """Obtiene los últimos mensajes de historial de chat para un teléfono.
    Si no hay historial, devuelve una lista vacía."""
    historial = db.query(ChatHistory).filter(
        ChatHistory.telefono == telefono
    ).order_by(ChatHistory.id.asc()).limit(limit).all()
    return historial if historial else []


@router.get("/perfil/{telefono}")
def get_perfil(telefono: str, db: Session = Depends(get_db)):
    """Obtiene los datos conversacionales del perfil de usuario"""
    perfil = db.query(UserProfile).filter(UserProfile.telefono == telefono).first()
    if not perfil:
        return {
            "telefono": telefono,
            "datos_conversacionales": None,
            "encontrado": False
        }
    return {
        "telefono": perfil.telefono,
        "datos_conversacionales": perfil.datos_conversacionales,
        "nombre_usuario": perfil.nombre_usuario,
        "ultima_interaccion": perfil.ultima_interaccion,
        "encontrado": True
    }


@router.post("/guardar-mensaje", response_model=ChatHistoryResponse, status_code=status.HTTP_201_CREATED)
def guardar_mensaje(telefono: str, rol: str, contenido: str, db: Session = Depends(get_db)):
    """Guarda un nuevo mensaje en el historial de chat.
    Acepta los datos como query parameters para compatibilidad con n8n."""
    db_mensaje = ChatHistory(telefono=telefono, rol=rol, contenido=contenido)
    db.add(db_mensaje)
    db.commit()
    db.refresh(db_mensaje)
    return db_mensaje


@router.post("/actualizar-perfil")
def actualizar_perfil(telefono: str, datos: UserProfileUpdate, db: Session = Depends(get_db)):
    """Actualiza o crea el perfil de usuario (Upsert)"""
    perfil = db.query(UserProfile).filter(UserProfile.telefono == telefono).first()
    
    if perfil:
        # Actualizar perfil existente
        update_data = datos.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(perfil, key, value)
        perfil.ultima_interaccion = datetime.now()
        db.commit()
        db.refresh(perfil)
        return {
            "telefono": perfil.telefono,
            "datos_conversacionales": perfil.datos_conversacionales,
            "nombre_usuario": perfil.nombre_usuario,
            "ultima_interaccion": perfil.ultima_interaccion,
            "accion": "actualizado"
        }
    else:
        # Crear nuevo perfil
        nuevo_perfil = UserProfile(
            telefono=telefono,
            nombre_usuario=datos.nombre_usuario,
            datos_conversacionales=datos.datos_conversacionales,
            ultima_interaccion=datetime.now()
        )
        db.add(nuevo_perfil)
        db.commit()
        db.refresh(nuevo_perfil)
        return {
            "telefono": nuevo_perfil.telefono,
            "datos_conversacionales": nuevo_perfil.datos_conversacionales,
            "nombre_usuario": nuevo_perfil.nombre_usuario,
            "ultima_interaccion": nuevo_perfil.ultima_interaccion,
            "accion": "creado"
        }
