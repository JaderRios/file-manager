from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil
import uuid

from database import SessionLocal, engine
from models import Base, Archivo, Usuario

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")
templates = Jinja2Templates(directory="templates")
# Servir la carpeta 'images' como estática
app.mount("/images", StaticFiles(directory="images"), name="images")

# ---------------------------------
# Redirigir la raíz al login
# ---------------------------------
@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/login")


# ---------------------------------
# Login
# ---------------------------------
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, error: str = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/login", response_class=HTMLResponse)
def login(request: Request, codigo: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    usuario_db = db.query(Usuario).filter(
        Usuario.codigo == codigo,  # validación por código
        Usuario.password == password,
        Usuario.estado == "activo"
    ).first()
    db.close()

    if usuario_db:
        return RedirectResponse(url=f"/upload?usuario_id={usuario_db.id}", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Código o contraseña incorrectos"})


# ---------------------------------
# Formulario de subida y lista de archivos
# ---------------------------------
@app.get("/upload", response_class=HTMLResponse)
def form_upload(request: Request, usuario_id: int):
    db = SessionLocal()
    usuario_db = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    archivos_db = db.query(Archivo).filter(Archivo.usuario_id == usuario_id).all()
    db.close()
    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "archivos": archivos_db,
            "usuario": usuario_db
        }
    )


# ---------------------------------
# Subir archivo
# ---------------------------------
@app.post("/upload", response_class=HTMLResponse)
async def upload_file(
    request: Request,
    usuario_id: int = Form(...),
    file: UploadFile = File(...),
    comentarios: str = Form("")
):
    ext = os.path.splitext(file.filename)[1]
    nombre_unico = f"{uuid.uuid4()}{ext}"
    file_location = os.path.join(UPLOAD_FOLDER, nombre_unico)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = SessionLocal()
    nuevo_archivo = Archivo(
        nombre=file.filename,
        ruta=nombre_unico,
        comentarios=comentarios,
        usuario_id=usuario_id
    )
    db.add(nuevo_archivo)
    db.commit()

    usuario_db = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    archivos_db = db.query(Archivo).filter(Archivo.usuario_id == usuario_id).all()
    db.close()

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
            "archivos": archivos_db,
            "mensaje": f"Archivo '{file.filename}' subido correctamente!",
            "usuario": usuario_db
        }
    )


@app.get("/logout")
def logout():
    return RedirectResponse(url="/login")


# ---------------------------------
# Eliminar archivo
# ---------------------------------
@app.get("/delete/{archivo_id}")
def delete_file(archivo_id: int, usuario_id: int):
    db = SessionLocal()
    archivo_db = db.query(Archivo).filter(Archivo.id == archivo_id).first()
    if archivo_db:
        # eliminar archivo físico
        file_path = os.path.join(UPLOAD_FOLDER, archivo_db.ruta)
        if os.path.exists(file_path):
            os.remove(file_path)
        # eliminar de la base de datos
        db.delete(archivo_db)
        db.commit()
    db.close()
    # redirigir al formulario de subida
    return RedirectResponse(url=f"/upload?usuario_id={usuario_id}", status_code=303)