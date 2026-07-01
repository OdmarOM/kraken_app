from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.tutor import Tutor
from app.schemas.tutor import TutorCreate, TutorUpdate, TutorResponse

router = APIRouter(prefix="/tutores", tags=["tutores"])


@router.post("/", response_model=TutorResponse, status_code=status.HTTP_201_CREATED)
def create_tutor(tutor: TutorCreate, db: Session = Depends(get_db)):
    db_tutor = Tutor(**tutor.model_dump())
    db.add(db_tutor)
    db.commit()
    db.refresh(db_tutor)
    return db_tutor


@router.get("/", response_model=List[TutorResponse])
def get_tutores(skip: int = 0, limit: int = 100, telefono: str = None, db: Session = Depends(get_db)):
    if telefono:
        tutor = db.query(Tutor).filter(Tutor.telefono == telefono).first()
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor no encontrado con ese teléfono")
        return [tutor]
    tutores = db.query(Tutor).offset(skip).limit(limit).all()
    return tutores


@router.get("/{tutor_id}", response_model=TutorResponse)
def get_tutor(tutor_id: int, db: Session = Depends(get_db)):
    tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not tutor:
        raise HTTPException(status_code=404, detail="Tutor no encontrado")
    return tutor


@router.put("/{tutor_id}", response_model=TutorResponse)
def update_tutor(tutor_id: int, tutor: TutorUpdate, db: Session = Depends(get_db)):
    db_tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not db_tutor:
        raise HTTPException(status_code=404, detail="Tutor no encontrado")
    
    update_data = tutor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_tutor, key, value)
    
    db.commit()
    db.refresh(db_tutor)
    return db_tutor


@router.delete("/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tutor(tutor_id: int, db: Session = Depends(get_db)):
    db_tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not db_tutor:
        raise HTTPException(status_code=404, detail="Tutor no encontrado")
    
    db.delete(db_tutor)
    db.commit()
    return None
