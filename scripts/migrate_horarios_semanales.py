"""
Migración para agregar soporte de horarios semanales a grupos
y crear la tabla de niveles.
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine, SessionLocal

def migrate():
    db = SessionLocal()
    
    try:
        # Crear tabla de niveles
        print("Creando tabla de niveles...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS niveles (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(50) UNIQUE NOT NULL,
                color VARCHAR(20) NOT NULL,
                activo BOOLEAN DEFAULT TRUE
            )
        """))
        
        # Crear tabla de horarios_grupos
        print("Creando tabla de horarios_grupos...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS horarios_grupos (
                id SERIAL PRIMARY KEY,
                grupo_id INTEGER NOT NULL REFERENCES grupos(id) ON DELETE CASCADE,
                dia_semana VARCHAR(20) NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL
            )
        """))
        
        # Crear índice para horarios_grupos
        print("Creando índices...")
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_horarios_grupos_grupo_id 
            ON horarios_grupos(grupo_id)
        """))
        
        # Migrar datos existentes de grupos a horarios_grupos
        print("Migrando horarios existentes...")
        result = db.execute(text("""
            SELECT id, dia_semana, hora_inicio, hora_fin 
            FROM grupos 
            WHERE dia_semana IS NOT NULL 
            AND hora_inicio IS NOT NULL 
            AND hora_fin IS NOT NULL
        """))
        
        grupos_migrados = 0
        for row in result:
            db.execute(text("""
                INSERT INTO horarios_grupos (grupo_id, dia_semana, hora_inicio, hora_fin)
                VALUES (:grupo_id, :dia_semana, :hora_inicio, :hora_fin)
            """), {
                'grupo_id': row[0],
                'dia_semana': row[1],
                'hora_inicio': row[2],
                'hora_fin': row[3]
            })
            grupos_migrados += 1
        
        print(f"Migrados {grupos_migrados} grupos a horarios semanales")
        
        # Eliminar columnas obsoletas de grupos (opcional, después de verificar migración)
        print("NOTA: Las columnas dia_semana, hora_inicio, hora_fin de grupos se pueden eliminar manualmente después de verificar la migración")
        
        db.commit()
        print("Migración completada exitosamente")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la migración: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
