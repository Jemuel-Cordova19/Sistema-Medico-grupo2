from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db

enrutador_autenticacion_medico = APIRouter(prefix="/autenticacion", tags=["Autenticación"])

@enrutador_autenticacion_medico.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    data = {}

    # Leer datos JSON o Formulario según lo envíe el navegador
    try:
        data = await request.json()
    except Exception:
        pass

    if not data:
        try:
            form_data = await request.form()
            data = dict(form_data)
        except Exception:
            pass

    # Capturar identificador y contraseña enviados por el frontend
    identificador = (
        data.get("correo_electronico_usuario") or 
        data.get("usuario") or 
        data.get("correo") or 
        data.get("username")
    )

    password = (
        data.get("contrasena_usuario") or 
        data.get("contraseña_usuario") or 
        data.get("contrasena") or 
        data.get("password")
    )

    if not identificador or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Por favor ingrese usuario y contraseña"
        )

    # Consulta a la tabla usuarios en Supabase
    query = text("""
        SELECT id, nombre, nombre_usuario, correo, password_hash, rol 
        FROM usuarios 
        WHERE (nombre_usuario = :id OR correo = :id) 
          AND password_hash = :pass 
          AND activo = TRUE
    """)
    
    resultado = db.execute(query, {"id": identificador, "pass": password}).fetchone()

    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )

    rol_texto = str(resultado.rol or "").strip().lower()

    # Mapeo de roles a identificadores numéricos para el frontend
    if "admin" in rol_texto:
        id_rol = 1
    elif "medico" in rol_texto or "médico" in rol_texto:
        id_rol = 2
    elif "recep" in rol_texto:
        id_rol = 3
    else:
        id_rol = 0

    return {
        "status": "success",
        "message": "Inicio de sesión exitoso",
        "identificador_rol_usuario": id_rol,
        "usuario": {
            "id": resultado.id,
            "nombre": resultado.nombre,
            "rol": rol_texto
        }
    }