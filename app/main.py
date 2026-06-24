from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.routers import auth, alumnos, grupos, instructores, tutores, niveles, leads, objetivos_semanales, evaluaciones, pagos, asistencias

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

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(alumnos.router)
app.include_router(grupos.router)
app.include_router(instructores.router)
app.include_router(tutores.router)
app.include_router(niveles.router)
app.include_router(leads.router)
app.include_router(objetivos_semanales.router)
app.include_router(evaluaciones.router)
app.include_router(pagos.router)
app.include_router(asistencias.router)


@app.get("/")
def root():
    return {"message": "Acuaticapp API - Sistema de Gestión para Escuela de Natación"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
