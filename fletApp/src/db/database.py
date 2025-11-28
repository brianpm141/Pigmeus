from sqlalchemy import create_engine
# CORRECCIÓN 1: Nueva forma de importar en SQLAlchemy 2.0
from sqlalchemy.orm import sessionmaker, declarative_base

# --- CONFIGURACIÓN DE CONEXIÓN ---
DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/pigmeus_db"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL, pool_recycle=3600, echo=False)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase Base
Base = declarative_base()

# --- DEPENDENCIA PARA INYECCIÓN ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FUNCIÓN DE INICIALIZACIÓN ---
def init_db():
    # CORRECCIÓN 2: La carpeta se llama 'db', no 'database'.
    # Importamos el módulo completo. Al importarlo, los modelos se registran en Base.
    import db.models 
    
    # Crea las tablas
    Base.metadata.create_all(bind=engine)