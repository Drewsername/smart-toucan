from fastapi import APIRouter, Query
from app.logic.reward_manager import RewardManager

router = APIRouter()

@router.post("/rewards/{reward_id}/redeem")
async def redeem_reward(reward_id: int, user_id: int = Query(...)):
    manager = RewardManager(user_id)
    await manager.load_reward(reward_id)
    return await manager.redeem()
