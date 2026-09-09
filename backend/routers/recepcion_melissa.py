from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def recepcion_status():
    return {"module": "Recepción", "author": "Melissa", "status": "active"}