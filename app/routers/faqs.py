from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.faq import FAQ
from app.schemas.faq import (
    FAQCreate, FAQUpdate, FAQResponse
)

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get("/", response_model=List[FAQResponse])
def get_faqs(
    activo: Optional[bool] = None,
    categoria: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtiene todas las FAQs con filtros opcionales"""
    query = db.query(FAQ)
    
    if activo is not None:
        query = query.filter(FAQ.activo == activo)
    
    if categoria:
        query = query.filter(FAQ.categoria == categoria)
    
    faqs = query.order_by(FAQ.orden.asc(), FAQ.creado_en.desc()).offset(skip).limit(limit).all()
    return faqs


@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(faq_id: int, db: Session = Depends(get_db)):
    """Obtiene una FAQ específica"""
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ no encontrada")
    return faq


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(faq: FAQCreate, db: Session = Depends(get_db)):
    """Crea una nueva FAQ"""
    nueva_faq = FAQ(**faq.model_dump())
    db.add(nueva_faq)
    db.commit()
    db.refresh(nueva_faq)
    return nueva_faq


@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    faq: FAQUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza una FAQ"""
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        raise HTTPException(status_code=404, detail="FAQ no encontrada")
    
    update_data = faq.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_faq, key, value)
    
    db.commit()
    db.refresh(db_faq)
    return db_faq


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """Elimina una FAQ"""
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        raise HTTPException(status_code=404, detail="FAQ no encontrada")
    
    db.delete(db_faq)
    db.commit()
    return None
