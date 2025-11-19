from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid

from database import SessionLocal, engine
from models import Base, Archivo

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Carpeta estática para mostrar archivos
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def form_upload(request: Request):
    db = SessionLocal()
    archivos_db = db.query(Archivo).all()  # Trae todos los registros de la BD
    db.close()

    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "archivos": archivos_db}  # PASAR OBJETOS COMPLETOS
    )

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    # Crear nombre único para el archivo (manteniendo extensión)
    ext = os.path.splitext(file.filename)[1]  # obtiene extensión
    nombre_unico = f"{uuid.uuid4()}{ext}"
    file_location = os.path.join(UPLOAD_FOLDER, nombre_unico)

    # Guardar archivo en carpeta uploads
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Guardar información en la base de datos
    db = SessionLocal()
    nuevo_archivo = Archivo(
        nombre=file.filename,  # nombre original para mostrar
        ruta=file_location,
        usuario_id=None
    )
    db.add(nuevo_archivo)
    db.commit()

    archivos_db = db.query(Archivo).all()
    db.close()

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "archivos": archivos_db, 
            "mensaje": f"Archivo '{file.filename}' subido correctamente!"
        }
    )
