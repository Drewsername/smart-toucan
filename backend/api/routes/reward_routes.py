from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.logic.reward_manager import RewardManager
from app.dependencies.auth import get_current_user_id
from app.schemas.reward import RewardCreate, RewardUpdate, RewardOut

router = APIRouter(prefix="/rewards", tags=["rewards"])

@router.post("/", response_model=RewardOut)
async def create_reward(
    reward_data: RewardCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.create_reward(reward_data.dict())

@router.get("/partner", response_model=List[RewardOut])
async def list_partner_rewards(
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.list_rewards_for_partner()

@router.get("/", response_model=List[RewardOut])
async def list_rewards(
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.list_rewards_for_user()

@router.put("/{reward_id}", response_model=RewardOut)
async def update_reward(
    reward_id: str,
    reward_data: RewardUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    return await RewardManager(current_user_id).update_reward(reward_id, reward_data.dict(exclude_unset=True))

@router.patch("/{reward_id}", response_model=RewardOut)
async def patch_reward(
    reward_id: str,
    data: dict,
    current_user_id: str = Depends(get_current_user_id)
):
    return await RewardManager(current_user_id).update_reward(reward_id, data)

@router.delete("/{reward_id}")
async def delete_reward(
    reward_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.delete_reward(reward_id)

@router.get("/{reward_id}", response_model=RewardOut)
async def get_reward(
    reward_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.get_reward_by_id(reward_id)

@router.post("/{reward_id}/redeem", response_model=RewardOut)
async def redeem_reward(
    reward_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = RewardManager(current_user_id)
    return await manager.redeem_reward(reward_id)
