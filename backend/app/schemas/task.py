# app/schemas/task.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class TimerStartMode(str, Enum):
    immediate = "immediate"
    onAccept = "onAccept"


class TaskStatus(str, Enum):
    pending = "PENDING"
    accepted = "ACCEPTED"
    declined = "DECLINED"
    completed = "COMPLETED"
    failed = "FAILED"
    expired = "EXPIRED"


class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    hasTimeLimit: bool = False
    timerStartMode: TimerStartMode = TimerStartMode.onAccept
    isVisible: bool = True
    hint: Optional[str] = Field(default=None, max_length=250)
    bonusPercentage: int = Field(default=0, ge=0)
    isBiddable: bool = False
    reservationPrice: Optional[int] = Field(default=None, ge=0)
    flatAwardPoints: Optional[int] = Field(default=None, ge=0)
    timeLimit: Optional[int] = Field(default=None, ge=1)
    acceptanceWindow: int = Field(default=60, ge=1)
    failurePenaltyPoints: int = Field(default=0, ge=0)


class TaskCreate(TaskBase):
    recipientId: Optional[str] = None  # not required from frontend



class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    hasTimeLimit: Optional[bool] = None
    timerStartMode: Optional[TimerStartMode] = None
    isVisible: Optional[bool] = None
    hint: Optional[str] = Field(default=None, max_length=250)
    bonusPercentage: Optional[int] = Field(default=None, ge=0)
    isBiddable: Optional[bool] = None
    reservationPrice: Optional[int] = Field(default=None, ge=0)
    flatAwardPoints: Optional[int] = Field(default=None, ge=0)
    timeLimit: Optional[int] = Field(default=None, ge=1)
    acceptanceWindow: Optional[int] = Field(default=None, ge=1)
    failurePenaltyPoints: Optional[int] = Field(default=None, ge=0)
    status: Optional[TaskStatus] = None


class TaskOut(TaskBase):
    id: str
    creatorId: str
    recipientId: str
    status: TaskStatus
    acceptanceDeadline: Optional[datetime] = None
    acceptedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    declinedAt: Optional[datetime] = None
    bidValue: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
