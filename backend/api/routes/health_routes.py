from fastapi import APIRouter
from app.logic.health_manager import HealthCheckManager

router = APIRouter()

@router.get("/health")
async def health_check():
    manager = HealthCheckManager()
    return await manager.get_health_report()
