#!/usr/bin/env python3
"""Script de migración para agregar columna grupo_id a la tabla alumnos"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    """Agrega la columna grupo_id a la tabla alumnos"""
    db = SessionLocal()
    
    try:
        # Verificar si la columna ya existe
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'alumnos' AND column_name = 'grupo_id'
        """))
        
        if result.fetchone():
            print("La columna grupo_id ya existe en la tabla alumnos")
            return
        
        # Agregar la columna
        db.execute(text("""
            ALTER TABLE alumnos 
            ADD COLUMN grupo_id INTEGER REFERENCES grupos(id)
        """))
        
        db.commit()
        print("Columna grupo_id agregada exitosamente a la tabla alumnos")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
