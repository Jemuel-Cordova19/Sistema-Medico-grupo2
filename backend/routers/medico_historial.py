from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.database import get_db
from pydantic import BaseModel

router = APIRouter(
    prefix="/medico",
    tags=["Medico e Historial Clinico"]
)

@router.get("/citas/{id_medico}")
async def obtener_citas_medico(id_medico: int, db: Session = Depends(get_db)):
    """
    Obtiene únicamente las citas asignadas al médico autenticado
    """
    try:
        # Consulta filtrando estrictamente por el ID del médico en la base de datos
        query = text("SELECT * FROM citas WHERE medico_id = :id_medico")
        resultado = db.execute(query, {"id_medico": id_medico}).mappings().all()
        citas = [dict(row) for row in resultado]

        if not citas:
            return []

        citas_formateadas = []
        for c in citas:
            item = {
                "id_cita": c.get("id") or c.get("id_cita", 1),
                "hora": str(c.get("hora", "09:00:00")),
                "paciente": c.get("nombre_paciente") or c.get("paciente") or "Paciente Asignado",
                "motivo": c.get("motivo_consulta") or c.get("motivo") or "Consulta General",
                "estado": c.get("estado") or "Pendiente"
            }
            citas_formateadas.append(item)

        return citas_formateadas

    except Exception as e:
        return [{"error_detallado": str(e)}]

from pydantic import BaseModel

# 1. Definir el esquema primero
class ConsultaSchema(BaseModel):
    id_cita: int
    presion_arterial: str
    temperatura: float
    peso: float
    frecuencia_cardiaca: int
    motivo_consulta: str
    sintomas: str
    antecedentes: str = ""
    alergias: str = ""
    diagnostico: str
    observaciones: str = ""
    medicamento: str
    presentacion: str = ""
    dosis: str = ""
    frecuencia: str = ""
    duracion: str = ""
    indicaciones_adicionales: str = ""

# 2. Definir el endpoint después
@router.post("/guardar-consulta")
async def guardar_consulta(datos: ConsultaSchema, db: Session = Depends(get_db)):
    try:
        # 1. Obtener paciente_id y medico_id usando únicamente la columna 'id'
        query_cita = text("SELECT paciente_id, medico_id FROM citas WHERE id = :id_cita")
        cita_res = db.execute(query_cita, {"id_cita": datos.id_cita}).fetchone()
        
        paciente_id = cita_res.paciente_id if cita_res and hasattr(cita_res, 'paciente_id') else 1
        medico_id = cita_res.medico_id if cita_res and hasattr(cita_res, 'medico_id') else 1

        # 2. Unificar los datos de la receta en el campo tratamiento_indicado
        tratamiento_completo = (
            f"Medicamento: {datos.medicamento} | "
            f"Presentación: {datos.presentacion} | "
            f"Dosis: {datos.dosis} | "
            f"Frecuencia: {datos.frecuencia} | "
            f"Duración: {datos.duracion} | "
            f"Indicaciones: {datos.indicaciones_adicionales} | "
            f"Alergias: {datos.alergias}"
        )

        # 3. Insertar la consulta
        query_insert = text("""
            INSERT INTO consultas (
                cita_id, paciente_id, medico_id, presion_arterial, temperatura, peso, frecuencia_cardiaca,
                motivo_consulta, sintomas, antecedentes, diagnostico, observaciones, tratamiento_indicado
            ) VALUES (
                :cita_id, :paciente_id, :medico_id, :presion, :temp, :peso, :hr,
                :motivo, :sintomas, :antecedentes, :diag, :obs, :tratamiento
            )
        """)
        
        db.execute(query_insert, {
            "cita_id": datos.id_cita,
            "paciente_id": paciente_id,
            "medico_id": medico_id,
            "presion": datos.presion_arterial,
            "temp": datos.temperatura,
            "peso": datos.peso,
            "hr": datos.frecuencia_cardiaca,
            "motivo": datos.motivo_consulta,
            "sintomas": datos.sintomas,
            "antecedentes": datos.antecedentes,
            "diag": datos.diagnostico,
            "obs": datos.observaciones,
            "tratamiento": tratamiento_completo
        })

        # 4. Actualizar el estado de la cita a "Atendida" usando únicamente 'id'
        query_update_cita = text("UPDATE citas SET estado = 'Atendida' WHERE id = :id_cita")
        db.execute(query_update_cita, {"id_cita": datos.id_cita})

        db.commit()
        return {"status": "success", "message": "Consulta registrada y cita atendida exitosamente"}

    except Exception as e:
        db.rollback()
        print("Error al guardar consulta:", e)
        raise HTTPException(status_code=500, detail=str(e))

# Aquí empieza la función para obtener y mostrar el historial médico del paciente desde la base de datos
@router.get("/historial-paciente/{paciente_id}")
async def obtener_historial_paciente(paciente_id: int, db: Session = Depends(get_db)):
    try:
        query = text("""
            SELECT c.id, c.fecha_hora, c.motivo_consulta, c.sintomas, 
                   c.diagnostico, c.tratamiento_indicado, c.presion_arterial, 
                   c.temperatura, c.peso, c.frecuencia_cardiaca
            FROM consultas c
            WHERE c.paciente_id = :paciente_id
            ORDER BY c.fecha_hora DESC
        """)
        resultado = db.execute(query, {"paciente_id": paciente_id}).mappings().all()
        return [dict(row) for row in resultado]
    except Exception as e:
        print("Error al obtener historial:", e)
        raise HTTPException(status_code=500, detail=str(e))