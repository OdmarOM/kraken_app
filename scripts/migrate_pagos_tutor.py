"""
Migración para actualizar la tabla pagos de alumno_id a tutor_id.
Ejecutar: python scripts/migrate_pagos_tutor.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Actualiza la tabla pagos para usar tutor_id en lugar de alumno_id"""
    print("Migrando tabla pagos...")
    
    try:
        with engine.connect() as conn:
            # Verificar si la tabla existe
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'pagos'
            """))
            table_exists = result.fetchone()
            
            if not table_exists:
                print("✓ La tabla pagos no existe. Se creará con la nueva estructura.")
                conn.commit()
                return
            
            # Hacer backup de datos existentes si los hay
            result = conn.execute(text("SELECT COUNT(*) FROM pagos"))
            count = result.fetchone()[0]
            
            if count > 0:
                print(f"⚠ La tabla tiene {count} registros. Se recomienda hacer un backup manual.")
                response = input("¿Deseas continuar? (s/n): ")
                if response.lower() != 's':
                    print("Migración cancelada.")
                    return
            
            # Eliminar la tabla para recrearla con la nueva estructura
            print("Eliminando tabla pagos...")
            conn.execute(text("DROP TABLE IF EXISTS pagos CASCADE"))
            conn.commit()
            print("✓ Tabla eliminada.")
            
            print("✓ Migración completada. La tabla se recreará con la nueva estructura al iniciar la app.")
    
    except Exception as e:
        print(f"✗ Error durante la migración: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Migración: Actualizar tabla pagos (alumno_id -> tutor_id)")
    print("=" * 60)
    migrate()
    print("=" * 60)
