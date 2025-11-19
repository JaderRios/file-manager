from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Archivo(Base):
    __tablename__ = "archivos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    ruta = Column(String(500), nullable=False)
    fecha = Column(TIMESTAMP, default=datetime.now)
    usuario_id = Column(Integer, nullable=True)  # hasta que agregues login
