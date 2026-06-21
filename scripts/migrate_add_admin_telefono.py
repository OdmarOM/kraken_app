#!/usr/bin/env python3
"""
Script de migración para agregar el campo telefono a la tabla admins
"""

import sys
import os

# Agregar el directorio padre al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text

def migrate_add_telefono():
    """Agrega la columna telefono a la tabla admins"""
    
    try:
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'admins' AND column_name = 'telefono'
            """))
            
            if result.fetchone():
                print("La columna 'telefono' ya existe en la tabla 'admins'")
                return
            
            # Agregar la columna telefono
            conn.execute(text("""
                ALTER TABLE admins 
                ADD COLUMN telefono VARCHAR(20)
            """))
            
            conn.commit()
            print("✓ Columna 'telefono' agregada exitosamente a la tabla 'admins'")
            
    except Exception as e:
        print(f"Error durante la migración: {e}")
        raise

if __name__ == "__main__":
    migrate_add_telefono()
