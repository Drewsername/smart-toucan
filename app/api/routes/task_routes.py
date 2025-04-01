# app/api/routes/task_routes.py
from fastapi import APIRouter, Depends
from typing import List
from app.logic.task_manager import TaskManager
from app.dependencies.auth import get_current_user_id
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut)
async def create_task(
    task_data: TaskCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.create_task(task_data.dict())


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.update_task(task_id, task_data.dict(exclude_unset=True))


@router.patch("/{task_id}", response_model=TaskOut)
async def patch_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.update_task(task_id, task_data.dict(exclude_unset=True))


@router.get("/", response_model=List[TaskOut])
async def list_my_tasks(
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.list_my_tasks()


@router.delete("/{task_id}", response_model=TaskOut)
async def delete_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.delete_task(task_id)


# 🔽 Recipient actions
@router.post("/{task_id}/recipient/accept", response_model=TaskOut)
async def recipient_accept_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.accept_task(task_id)


@router.post("/{task_id}/recipient/decline", response_model=TaskOut)
async def recipient_decline_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.decline_task(task_id)


@router.post("/{task_id}/recipient/complete", response_model=TaskOut)
async def recipient_complete_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.complete_task(task_id)


@router.post("/{task_id}/recipient/bid", response_model=TaskOut)
async def recipient_bid_task(
    task_id: str,
    bid: int,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.bid_on_task(task_id, bid)


# 🔽 Creator actions
@router.post("/{task_id}/creator/validate", response_model=TaskOut)
async def creator_validate_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.creator_validate_task(task_id)


@router.post("/{task_id}/creator/complete", response_model=TaskOut)
async def creator_force_complete_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    manager = TaskManager(current_user_id)
    return await manager.creator_force_complete(task_id)
