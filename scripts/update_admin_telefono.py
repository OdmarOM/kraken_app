#!/usr/bin/env python3
"""
Script para actualizar el teléfono del admin existente
"""

import sys
import os

# Agregar el directorio padre al path para poder importar los módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.admin import Admin

def update_admin_telefono():
    """Actualiza el teléfono del admin existente"""
    
    try:
        db = SessionLocal()
        admin = db.query(Admin).filter(Admin.username == 'admin').first()
        
        if admin:
            admin.telefono = '555-9999'
            db.commit()
            print('Admin actualizado con teléfono: 555-9999')
        else:
            print('Admin no encontrado')
            
    except Exception as e:
        print(f"Error durante la actualización: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_telefono()
