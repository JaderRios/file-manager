from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Conexión a files_db con el usuario que creamos
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://jader:123456@localhost/files_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
