from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def admin_status():
    return {"module": "Administración", "author": "Jimena", "status": "active"}