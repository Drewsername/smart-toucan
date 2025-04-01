from fastapi import APIRouter, Depends
from app.logic.pairing_manager import PairingManager
from app.dependencies.auth import get_current_user_id
from app.schemas.pairing import PairingCodeUse, PairingOut

router = APIRouter(prefix="/pairing", tags=["pairing"])

@router.post("/generate", response_model=PairingOut)
async def generate_code(
    current_user_id: str = Depends(get_current_user_id)
):
    manager = PairingManager(current_user_id)
    code = await manager.generate_code()
    return code

@router.post("/use", response_model=dict)
async def use_pairing_code(
    body: PairingCodeUse,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = PairingManager(current_user_id)
    return await manager.use_code(body.code)

@router.post("/unpair", response_model=dict)
async def unpair(
    current_user_id: str = Depends(get_current_user_id)
):
    manager = PairingManager(current_user_id)
    return await manager.unpair()
