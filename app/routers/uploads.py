from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
from pathlib import Path
from datetime import datetime

router = APIRouter(prefix="/api/uploads", tags=["uploads"])

# Configurar directorios de uploads
UPLOAD_DIR = Path("/opt/acuaticapp-backend/uploads")
COMPROBANTES_DIR = UPLOAD_DIR / "comprobantes"
EVENTOS_DIR = UPLOAD_DIR / "eventos"

# Crear directorios si no existen
COMPROBANTES_DIR.mkdir(parents=True, exist_ok=True)
EVENTOS_DIR.mkdir(parents=True, exist_ok=True)

# Tipos de archivos permitidos
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{unique_id}{ext}"


@router.post("/comprobantes")
async def upload_comprobante(file: UploadFile = File(...)):
    """Sube un comprobante de pago"""
    if not file:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
    
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Leer contenido y verificar tamaño
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo de 10MB")
    
    # Generar nombre único
    filename = generate_unique_filename(file.filename)
    file_path = COMPROBANTES_DIR / filename
    
    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": filename,
        "url": f"/uploads/comprobantes/{filename}",
        "message": "Comprobante subido exitosamente"
    }


@router.post("/eventos")
async def upload_evento_image(file: UploadFile = File(...)):
    """Sube una imagen para un evento/aviso"""
    if not file:
        raise HTTPException(status_code=400, detail="No se proporcionó ningún archivo")
    
    ext = get_file_extension(file.filename)
    if ext not in {".jpg", ".jpeg", ".png", ".gif"}:
        raise HTTPException(
            status_code=400, 
            detail="Tipo de archivo no permitido. Solo se permiten imágenes: jpg, jpeg, png, gif"
        )
    
    # Leer contenido y verificar tamaño
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo excede el tamaño máximo de 10MB")
    
    # Generar nombre único
    filename = generate_unique_filename(file.filename)
    file_path = EVENTOS_DIR / filename
    
    # Guardar archivo
    with open(file_path, "wb") as f:
        f.write(content)
    
    return {
        "filename": filename,
        "url": f"/uploads/eventos/{filename}",
        "message": "Imagen subida exitosamente"
    }


@router.get("/comprobantes/{filename}")
async def get_comprobante(filename: str):
    """Obtiene un comprobante de pago"""
    file_path = COMPROBANTES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)


@router.get("/eventos/{filename}")
async def get_evento_image(filename: str):
    """Obtiene una imagen de evento"""
    file_path = EVENTOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return FileResponse(file_path)


@router.delete("/comprobantes/{filename}")
async def delete_comprobante(filename: str):
    """Elimina un comprobante de pago"""
    file_path = COMPROBANTES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    os.remove(file_path)
    return {"message": "Comprobante eliminado exitosamente"}


@router.delete("/eventos/{filename}")
async def delete_evento_image(filename: str):
    """Elimina una imagen de evento"""
    file_path = EVENTOS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    
    os.remove(file_path)
    return {"message": "Imagen eliminada exitosamente"}
