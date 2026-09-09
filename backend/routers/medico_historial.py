from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def medico_status():
    return {"module": "Atención Médica e Historial", "status": "active"} 