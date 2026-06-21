"""
Script para sembrar los niveles iniciales de gorra
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.nivel import Nivel

def seed_niveles():
    db = SessionLocal()
    
    try:
        niveles_iniciales = [
            {"nombre": "Blanca", "color": "#FFFFFF"},
            {"nombre": "Amarilla", "color": "#FFD700"},
            {"nombre": "Roja", "color": "#FF0000"},
            {"nombre": "Azul", "color": "#0000FF"},
            {"nombre": "Plateada", "color": "#C0C0C0"},
            {"nombre": "Dorada", "color": "#FFD700"},
            {"nombre": "Negra", "color": "#000000"},
            {"nombre": "Adultos", "color": "#808080"},
        ]
        
        for nivel_data in niveles_iniciales:
            # Verificar si ya existe
            existing = db.query(Nivel).filter(Nivel.nombre == nivel_data["nombre"]).first()
            if not existing:
                nivel = Nivel(**nivel_data)
                db.add(nivel)
                print(f"Nivel '{nivel_data['nombre']}' creado")
            else:
                print(f"Nivel '{nivel_data['nombre']}' ya existe")
        
        db.commit()
        print("Sembrado de niveles completado")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante el sembrado: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_niveles()
