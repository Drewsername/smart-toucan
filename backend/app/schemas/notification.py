from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    userId: str
    type: str # e.g., 'TASK_COMPLETED', 'REWARD_REDEEMED', 'NEW_TASK', 'TASK_TIMEOUT', 'PAIRING_UPDATE'
    message: str
    referenceLink: Optional[str] = Field(
        None,
        description="Relative URL path to referenced resource (e.g. '/tasks/123')"
    )

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: str
    isRead: bool
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True