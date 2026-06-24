#!/usr/bin/env python3
"""
Migración: Agregar campos estáticos a tabla asistencias
Preserva el estado al momento del registro para historial
"""

import sys
sys.path.insert(0, '/opt/acuaticapp-backend')

from app.database import engine
from sqlalchemy import text

def migrate():
    print("=" * 60)
    print("Migración: Agregar campos estáticos a asistencias")
    print("=" * 60)
    
    conn = engine.connect()
    
    try:
        # Verificar si los campos ya existen
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'asistencias' 
            AND column_name IN ('instructor_id', 'nombre_grupo', 'nivel_gorra', 'nombre_instructor', 'nombre_alumno')
        """))
        existing_columns = [row[0] for row in result]
        
        print(f"Columnas existentes: {existing_columns}")
        
        # Agregar instructor_id si no existe
        if 'instructor_id' not in existing_columns:
            print("Agregando columna instructor_id...")
            conn.execute(text("""
                ALTER TABLE asistencias 
                ADD COLUMN instructor_id INTEGER REFERENCES instructores(id) ON DELETE SET NULL
            """))
            conn.execute(text("CREATE INDEX ix_asistencias_instructor_id ON asistencias(instructor_id)"))
            print("✓ Columna instructor_id agregada")
        else:
            print("- Columna instructor_id ya existe")
        
        # Agregar nombre_grupo si no existe
        if 'nombre_grupo' not in existing_columns:
            print("Agregando columna nombre_grupo...")
            conn.execute(text("""
                ALTER TABLE asistencias 
                ADD COLUMN nombre_grupo VARCHAR(100)
            """))
            print("✓ Columna nombre_grupo agregada")
        else:
            print("- Columna nombre_grupo ya existe")
        
        # Agregar nivel_gorra si no existe
        if 'nivel_gorra' not in existing_columns:
            print("Agregando columna nivel_gorra...")
            conn.execute(text("""
                ALTER TABLE asistencias 
                ADD COLUMN nivel_gorra VARCHAR(50)
            """))
            print("✓ Columna nivel_gorra agregada")
        else:
            print("- Columna nivel_gorra ya existe")
        
        # Agregar nombre_instructor si no existe
        if 'nombre_instructor' not in existing_columns:
            print("Agregando columna nombre_instructor...")
            conn.execute(text("""
                ALTER TABLE asistencias 
                ADD COLUMN nombre_instructor VARCHAR(100)
            """))
            print("✓ Columna nombre_instructor agregada")
        else:
            print("- Columna nombre_instructor ya existe")
        
        # Agregar nombre_alumno si no existe
        if 'nombre_alumno' not in existing_columns:
            print("Agregando columna nombre_alumno...")
            conn.execute(text("""
                ALTER TABLE asistencias 
                ADD COLUMN nombre_alumno VARCHAR(100)
            """))
            print("✓ Columna nombre_alumno agregada")
        else:
            print("- Columna nombre_alumno ya existe")
        
        conn.commit()
        print("\n✓ Migración completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error durante la migración: {e}")
        raise
    finally:
        conn.close()
    
    print("=" * 60)

if __name__ == "__main__":
    migrate()
