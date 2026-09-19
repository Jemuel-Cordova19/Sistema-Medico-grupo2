import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Carga las variables del archivo .env ubicado en la raíz del proyecto
load_dotenv()

# Lee la variable DATABASE_URL del archivo .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Verifica si existe la URL; si no existe, lanza un error claro
if not DATABASE_URL:
    raise ValueError("No se encontró la variable DATABASE_URL en el archivo .env")

# Ajusta el nombre del protocolo en la URL en caso de que empiece con postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Crea el motor de conexión que se comunica directamente con PostgreSQL en Supabase
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Crea el fabricador de sesiones para realizar operaciones (insertar, consultar, actualizar)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base principal para crear los modelos de las tablas en Python
Base = declarative_base()

# Función que abre una sesión de base de datos cuando llega una petición y la cierra al terminar
def get_db():
    db = SessionLocal()  # Abre la sesión
    try:
        yield db         # Entrega la sesión a la función que la solicitó
    finally:
        db.close()       # Cierra la sesión para evitar saturar la base de datos