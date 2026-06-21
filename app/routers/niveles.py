from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.nivel import Nivel
from app.schemas.nivel import NivelCreate, NivelUpdate, NivelResponse

router = APIRouter(prefix="/niveles", tags=["niveles"])

@router.get("/", response_model=List[NivelResponse])
def get_niveles(db: Session = Depends(get_db)):
    niveles = db.query(Nivel).filter(Nivel.activo == True).all()
    return niveles

@router.get("/{nivel_id}", response_model=NivelResponse)
def get_nivel(nivel_id: int, db: Session = Depends(get_db)):
    nivel = db.query(Nivel).filter(Nivel.id == nivel_id).first()
    if not nivel:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    return nivel

@router.post("/", response_model=NivelResponse, status_code=status.HTTP_201_CREATED)
def create_nivel(nivel: NivelCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe un nivel con ese nombre
    existing = db.query(Nivel).filter(Nivel.nombre == nivel.nombre).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un nivel con ese nombre")
    
    db_nivel = Nivel(**nivel.model_dump())
    db.add(db_nivel)
    db.commit()
    db.refresh(db_nivel)
    return db_nivel

@router.put("/{nivel_id}", response_model=NivelResponse)
def update_nivel(nivel_id: int, nivel: NivelUpdate, db: Session = Depends(get_db)):
    db_nivel = db.query(Nivel).filter(Nivel.id == nivel_id).first()
    if not db_nivel:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    
    update_data = nivel.model_dump(exclude_unset=True)
    
    # Si se cambia el nombre, verificar que no exista otro con ese nombre
    if 'nombre' in update_data:
        existing = db.query(Nivel).filter(
            Nivel.nombre == update_data['nombre'],
            Nivel.id != nivel_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un nivel con ese nombre")
    
    for key, value in update_data.items():
        setattr(db_nivel, key, value)
    
    db.commit()
    db.refresh(db_nivel)
    return db_nivel

@router.delete("/{nivel_id}")
def delete_nivel(nivel_id: int, db: Session = Depends(get_db)):
    db_nivel = db.query(Nivel).filter(Nivel.id == nivel_id).first()
    if not db_nivel:
        raise HTTPException(status_code=404, detail="Nivel no encontrado")
    
    # Soft delete
    db_nivel.activo = False
    db.commit()
    return {"message": "Nivel eliminado correctamente"}
