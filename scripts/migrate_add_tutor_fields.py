"""
Migración para agregar campos de tutor a la tabla evaluaciones.
Ejecutar: python scripts/migrate_add_tutor_fields.py
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from sqlalchemy import text

def migrate():
    """Agrega las columnas presentado_al_tutor y fecha_entrega_tutor a la tabla evaluaciones."""
    print("Migrando tabla evaluaciones...")
    
    try:
        with engine.connect() as conn:
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'evaluaciones' 
                AND column_name IN ('presentado_al_tutor', 'fecha_entrega_tutor')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'presentado_al_tutor' in existing_columns and 'fecha_entrega_tutor' in existing_columns:
                print("✓ Las columnas ya existen. No se requiere migración.")
                return
            
            # Agregar columnas si no existen
            if 'presentado_al_tutor' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE evaluaciones 
                    ADD COLUMN presentado_al_tutor BOOLEAN DEFAULT FALSE NOT NULL
                """))
                print("✓ Columna presentado_al_tutor agregada.")
            
            if 'fecha_entrega_tutor' not in existing_columns:
                conn.execute(text("""
                    ALTER TABLE evaluaciones 
                    ADD COLUMN fecha_entrega_tutor TIMESTAMP WITH TIME ZONE
                """))
                print("✓ Columna fecha_entrega_tutor agregada.")
            
            conn.commit()
            print("✓ Migración completada exitosamente.")
    
    except Exception as e:
        print(f"✗ Error durante la migración: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Migración: Agregar campos de tutor a evaluaciones")
    print("=" * 60)
    migrate()
    print("=" * 60)
