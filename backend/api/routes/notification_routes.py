from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.logic.notification_manager import NotificationManager
from app.schemas.notification import Notification
from app.dependencies.auth import get_current_user_id 

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}},
)

# Removed dependency function, manager will be instantiated directly in routes

@router.get("/", response_model=List[Notification])
async def read_user_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user_id: str = Depends(get_current_user_id), # Corrected dependency and type hint
    # Removed manager dependency injection
):
    """
    Retrieve notifications for the current user.
    """
    # Instantiate manager directly using the user ID string
    manager = NotificationManager(current_user_id)
    notifications = await manager.get_notifications_for_user(
        user_id=current_user_id, skip=skip, limit=limit
    )
    return notifications

@router.patch("/{notification_id}/read", response_model=Notification)
async def mark_notification_as_read(
    notification_id: int,
    current_user_id: str = Depends(get_current_user_id), # Corrected dependency and type hint
    # Removed manager dependency injection
):
    """
    Mark a specific notification as read for the current user.
    """
    # Instantiate manager directly using the user ID string
    manager = NotificationManager(current_user_id)
    notification = await manager.mark_notification_as_read(
        notification_id=notification_id, user_id=current_user_id
    )
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found or you do not have permission to access it.",
        )
    return notification

@router.patch("/read-all", response_model=Dict[str, Any])
async def mark_all_notifications_as_read(
    current_user_id: str = Depends(get_current_user_id), # Corrected dependency and type hint
    # Removed manager dependency injection
):
    """
    Mark all unread notifications as read for the current user.
    """
    # Instantiate manager directly using the user ID string
    manager = NotificationManager(current_user_id)
    updated_count = await manager.mark_all_notifications_as_read(
        user_id=current_user_id
    )
    return {"message": "All notifications marked as read", "count": updated_count}