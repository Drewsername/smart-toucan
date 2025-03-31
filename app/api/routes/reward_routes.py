from fastapi import APIRouter, Request, Depends
from app.dependencies.auth import get_current_user_id
from app.logic.reward_manager import RewardManager

router = APIRouter()

@router.post("/rewards/{reward_id}/redeem")
async def redeem_reward(reward_id: int, user_id: str = Depends(get_current_user_id)):
    manager = RewardManager(user_id)
    await manager.load_reward(reward_id)
    return await manager.redeem()
