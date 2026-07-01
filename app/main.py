from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.config import settings
from app.routers import auth, alumnos, grupos, instructores, tutores, niveles, leads, objetivos_semanales, evaluaciones, pagos, asistencias, avisos_eventos, faqs, uploads, busqueda, chat
from pathlib import Path

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Acuaticapp API",
    description="Sistema de Gestión para Escuela de Natación",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes para acceso desde cualquier dispositivo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio de uploads como archivos estáticos (antes de las rutas API)
uploads_dir = Path("/opt/acuaticapp-backend/uploads")
if uploads_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Incluir routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(alumnos.router, prefix="/api")
app.include_router(grupos.router, prefix="/api")
app.include_router(instructores.router, prefix="/api")
app.include_router(tutores.router, prefix="/api")
app.include_router(niveles.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(objetivos_semanales.router, prefix="/api")
app.include_router(evaluaciones.router, prefix="/api")
app.include_router(pagos.router, prefix="/api")
app.include_router(asistencias.router, prefix="/api")
app.include_router(avisos_eventos.router, prefix="/api")
app.include_router(faqs.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(busqueda.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Acuaticapp API - Sistema de Gestión para Escuela de Natación"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
