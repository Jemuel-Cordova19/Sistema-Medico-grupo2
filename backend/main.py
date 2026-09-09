from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importación de routers por integrante
from backend.routers import auth_medico, admin_jimena, recepcion_melissa, medico_historial

app = FastAPI(
    title="Sistema Médico G2 API",
    description="API RESTful para gestión de clínica médica",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(auth_medico.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(admin_jimena.router, prefix="/api/admin", tags=["Administración (Jimena)"])
app.include_router(recepcion_melissa.router, prefix="/api/recepcion", tags=["Recepción (Melissa)"])
app.include_router(medico_historial.router, prefix="/api/medico", tags=["Médico & Historial"])

@app.get("/api")
def root():
    return {"status": "ok", "message": "API del Sistema Médico G2 funcionando correctamente"}