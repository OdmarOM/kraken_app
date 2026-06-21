"""
Script de inicialización de la base de datos.
Crea todas las tablas definidas en los modelos SQLAlchemy.
"""
import sys
import os

# Agregar el directorio raíz al path para importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, Base, SessionLocal
from app.models import (
    Admin,
    Instructor,
    Tutor,
    Alumno,
    Grupo,
    Asistencia,
    Evaluacion,
    Pago,
    ObjetivoSemanal,
    Lead
)
import bcrypt


def init_db():
    """Crea todas las tablas en la base de datos."""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente.")


def create_admin_user():
    """Crea un usuario admin por defecto si no existe."""
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        existing_admin = db.query(Admin).filter(Admin.username == "admin").first()
        if existing_admin:
            print("✓ El usuario admin ya existe.")
            return

        # Crear usuario admin por defecto
        hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Cambiar en producción
        admin = Admin(
            username="admin",
            hashed_password=hashed_password,
            email="admin@acuaticapp.com",
            nombre_completo="Administrador Principal",
            activo=True
        )
        db.add(admin)
        db.commit()
        print("✓ Usuario admin creado exitosamente (username: admin, password: admin123)")
        print("  ⚠ IMPORTANTE: Cambia la contraseña por defecto en producción.")
    except Exception as e:
        print(f"✗ Error al crear usuario admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("Inicialización de Base de Datos - Acuaticapp")
    print("=" * 60)
    
    init_db()
    create_admin_user()
    
    print("=" * 60)
    print("Inicialización completada.")
    print("=" * 60)
