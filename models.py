from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Enum
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    email = Column(String(150))
    password = Column(String(255))
    codigo = Column(String(20), unique=True, nullable=False)
    estado = Column(Enum("activo", "inactivo"), default="activo")

    archivos = relationship("Archivo", back_populates="usuario")  # relación con Archivo


class Archivo(Base):
    __tablename__ = "archivos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    ruta = Column(String(500), nullable=False)
    comentarios = Column(Text, nullable=True)  # nuevo campo
    fecha = Column(TIMESTAMP, default=datetime.datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    usuario = relationship("Usuario", back_populates="archivos")  # relación inversa
