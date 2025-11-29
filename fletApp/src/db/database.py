from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- CAMBIO A POSTGRESQL ---
# Formato: postgresql+psycopg2://USUARIO:PASSWORD@HOST:PUERTO/DB
DATABASE_URL = "postgresql+psycopg2://postgres:1234@127.0.0.1:5432/pigmeus_db?sslmode=disable"
# Crear el motor 
# Nota: Postgres maneja el pool de forma distinta, pero la config base funciona bien.
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import db.models 
    Base.metadata.create_all(bind=engine)