#!/usr/bin/env python3
"""Script para poblar la base de datos con datos de prueba"""

import sys
import os
from datetime import date, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.tutor import Tutor
from app.models.instructor import Instructor
from app.models.grupo import Grupo
from app.models.alumno import Alumno

def seed_data():
    """Puebla la base de datos con datos de prueba"""
    db = SessionLocal()
    
    try:
        # Crear tutores
        tutores = []
        tutor_data = [
            {"nombre": "Juan Pérez", "telefono": "555-0101", "email": "juan.perez@email.com", "direccion": "Calle 123, Ciudad"},
            {"nombre": "María García", "telefono": "555-0102", "email": "maria.garcia@email.com", "direccion": "Avenida 456, Ciudad"},
            {"nombre": "Carlos López", "telefono": "555-0103", "email": "carlos.lopez@email.com", "direccion": "Plaza 789, Ciudad"},
        ]
        
        for data in tutor_data:
            tutor = Tutor(**data, activo=True)
            db.add(tutor)
            db.flush()
            tutores.append(tutor)
        db.commit()
        print("✓ Tutores creados")
        
        # Crear instructores
        instructores = []
        instructor_data = [
            {"nombre": "Roberto Sánchez", "telefono": "555-0201", "email": "roberto.sanchez@email.com"},
            {"nombre": "Ana Martínez", "telefono": "555-0202", "email": "ana.martinez@email.com"},
        ]
        
        for data in instructor_data:
            instructor = Instructor(**data, activo=True)
            db.add(instructor)
            db.flush()
            instructores.append(instructor)
        db.commit()
        print("✓ Instructores creados")
        
        # Crear grupos
        grupos = []
        grupo_data = [
            {"nombre": "Principiantes Lunes", "nivel_asociado": "Blanca", "dia_semana": "Lunes", "hora_inicio": time(16, 0), "hora_fin": time(17, 0), "cupo_maximo": 10, "instructor_id": instructores[0].id},
            {"nombre": "Intermedios Miércoles", "nivel_asociado": "Amarilla", "dia_semana": "Miércoles", "hora_inicio": time(17, 0), "hora_fin": time(18, 0), "cupo_maximo": 8, "instructor_id": instructores[0].id},
            {"nombre": "Avanzados Viernes", "nivel_asociado": "Roja", "dia_semana": "Viernes", "hora_inicio": time(18, 0), "hora_fin": time(19, 0), "cupo_maximo": 6, "instructor_id": instructores[1].id},
        ]
        
        for data in grupo_data:
            grupo = Grupo(**data, activo=True)
            db.add(grupo)
            db.flush()
            grupos.append(grupo)
        db.commit()
        print("✓ Grupos creados")
        
        # Crear alumnos
        alumnos = []
        alumno_data = [
            {"nombre": "Pedro Pérez", "tutor_id": tutores[0].id, "grupo_id": grupos[0].id, "fecha_nacimiento": date(2018, 5, 15), "edad": 6, "nivel_gorra": "Blanca"},
            {"nombre": "Sofía García", "tutor_id": tutores[1].id, "grupo_id": grupos[0].id, "fecha_nacimiento": date(2017, 8, 20), "edad": 7, "nivel_gorra": "Blanca"},
            {"nombre": "Diego López", "tutor_id": tutores[2].id, "grupo_id": grupos[1].id, "fecha_nacimiento": date(2015, 3, 10), "edad": 9, "nivel_gorra": "Amarilla"},
            {"nombre": "Elena Martínez", "tutor_id": tutores[0].id, "grupo_id": grupos[1].id, "fecha_nacimiento": date(2016, 11, 5), "edad": 8, "nivel_gorra": "Amarilla"},
            {"nombre": "Miguel Sánchez", "tutor_id": tutores[1].id, "grupo_id": grupos[2].id, "fecha_nacimiento": date(2013, 7, 25), "edad": 11, "nivel_gorra": "Roja"},
        ]
        
        for data in alumno_data:
            alumno = Alumno(**data, activo=True)
            db.add(alumno)
            db.flush()
            alumnos.append(alumno)
        db.commit()
        print("✓ Alumnos creados")
        
        print("\n============================================================")
        print("Datos de prueba creados exitosamente")
        print("============================================================")
        print(f"Tutores: {len(tutores)}")
        print(f"Instructores: {len(instructores)}")
        print(f"Grupos: {len(grupos)}")
        print(f"Alumnos: {len(alumnos)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la creación de datos: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
