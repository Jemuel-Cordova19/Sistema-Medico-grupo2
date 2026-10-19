# Importamos la clase FastAPI y las dependencias necesarias
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importamos la base de datos, el motor y la base declarativa
from backend.database import get_db, engine, Base
from backend import models

# Importamos los routers de autenticación y de historial médico
from backend.routers.auth_medico import enrutador_autenticacion_medico
from backend.routers import medico_historial

# Esta instrucción crea automáticamente todas las tablas en Supabase
Base.metadata.create_all(bind=engine)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="Sistema Médico API - Grupo 2",
    description="API REST para la gestión de citas, consultas, recetas y caja",
    version="1.0.0"
)

# Configuración de CORS para permitir la conexión desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permite peticiones de cualquier origen
    allow_credentials=True,     # Permite el envío de credenciales
    allow_methods=["*"],        # Permite todos los métodos HTTP
    allow_headers=["*"],        # Permite todos los encabezados HTTP
)

# -------------------------------------------------------------
# INCLUSIÓN DE ROUTERS (ENRUTADORES DEL SISTEMA)
# -------------------------------------------------------------
app.include_router(enrutador_autenticacion_medico)
app.include_router(medico_historial.router)

# -------------------------------------------------------------
# RUTAS DE COMPROBACIÓN DEL SERVIDOR
# -------------------------------------------------------------

# Ruta raíz de comprobación de estado del servidor
@app.get("/")
def read_root():
    return {"status": "ok", "message": "API del Sistema Médico en ejecución"}

# Ruta para verificar la comunicación directa con PostgreSQL en Supabase
@app.get("/test-db")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT version();")).fetchone()
        return {
            "status": "success",
            "message": "Conexión exitosa a Supabase PostgreSQL",
            "db_version": result[0]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al conectar con la base de datos: {str(e)}"
        )
