from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.instructor import Instructor
from app.schemas.instructor import InstructorCreate, InstructorUpdate, InstructorResponse

router = APIRouter(prefix="/instructores", tags=["instructores"])


@router.post("/", response_model=InstructorResponse, status_code=status.HTTP_201_CREATED)
def create_instructor(instructor: InstructorCreate, db: Session = Depends(get_db)):
    db_instructor = Instructor(**instructor.model_dump())
    db.add(db_instructor)
    db.commit()
    db.refresh(db_instructor)
    return db_instructor


@router.get("/", response_model=List[InstructorResponse])
def get_instructores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    instructores = db.query(Instructor).offset(skip).limit(limit).all()
    return instructores


@router.get("/{instructor_id}", response_model=InstructorResponse)
def get_instructor(instructor_id: int, db: Session = Depends(get_db)):
    instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    if not instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    return instructor


@router.put("/{instructor_id}", response_model=InstructorResponse)
def update_instructor(instructor_id: int, instructor: InstructorUpdate, db: Session = Depends(get_db)):
    db_instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    if not db_instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    update_data = instructor.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_instructor, key, value)
    
    db.commit()
    db.refresh(db_instructor)
    return db_instructor


@router.delete("/{instructor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_instructor(instructor_id: int, db: Session = Depends(get_db)):
    db_instructor = db.query(Instructor).filter(Instructor.id == instructor_id).first()
    if not db_instructor:
        raise HTTPException(status_code=404, detail="Instructor no encontrado")
    
    db.delete(db_instructor)
    db.commit()
    return None
