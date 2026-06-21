# Acuaticapp - Sistema de Gestión para Escuela de Natación

Backend en FastAPI para la administración integral de una escuela de natación.

## Stack Tecnológico
- **Backend:** Python FastAPI
- **Base de Datos:** PostgreSQL con SQLAlchemy ORM
- **Orquestación:** n8n (conectado vía Evolution API para WhatsApp)

## Estructura del Proyecto
```
acuaticapp/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point de FastAPI
│   ├── config.py            # Configuración de la aplicación
│   ├── database.py          # Conexión a la base de datos
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── api/                 # Endpoints de la API
│   └── services/            # Lógica de negocio
├── alembic/                 # Migraciones de base de datos
├── scripts/                 # Scripts de utilidad
├── requirements.txt
└── .env.example
```

## Instalación
```bash
pip install -r requirements.txt
cp .env.example .env
# Editar .env con las credenciales de la base de datos
```

## Ejecución
```bash
uvicorn app.main:app --reload
```

## API Documentation
Al iniciar el servidor, la documentación estará disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
