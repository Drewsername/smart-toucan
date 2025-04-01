# app/schemas/reward.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ScalingFunction(str, Enum):
    linear = "linear"
    exponential = "exponential"
    flat = "flat"


class RewardBase(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    points: Optional[int] = Field(default=None, ge=0)
    categoryId: Optional[str] = None
    redemptionUnit: Optional[str] = Field(default=None, max_length=50)
    redemptionUnitStepSize: Optional[int] = Field(default=None, ge=1)
    priceScalingFunction: Optional[ScalingFunction] = None
    scalingFactor: Optional[float] = Field(default=None, ge=0)
    dailyLimit: Optional[int] = Field(default=None, ge=0)
    weeklyLimit: Optional[int] = Field(default=None, ge=0)
    monthlyLimit: Optional[int] = Field(default=None, ge=0)
    yearlyLimit: Optional[int] = Field(default=None, ge=0)
    isUnlimited: Optional[bool] = None
    visible: Optional[bool] = None
    unlocked: Optional[bool] = None


class RewardCreate(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    points: Optional[int] = Field(default=None, ge=0)
    categoryId: Optional[str] = None
    redemptionUnit: str = Field(..., max_length=50)
    redemptionUnitStepSize: int = Field(..., ge=1)
    priceScalingFunction: ScalingFunction
    scalingFactor: float = Field(..., ge=0)
    dailyLimit: Optional[int] = Field(default=None, ge=0)
    isUnlimited: bool
    visible: bool
    unlocked: bool

    @model_validator(mode="after")
    def validate_points_requirement(self) -> "RewardCreate":
        if not self.isUnlimited and self.points is None:
            raise ValueError("You must provide 'points' when the reward is not unlimited.")
        return self


class RewardUpdate(RewardBase):
    pass


class RewardOut(RewardBase):
    id: str
    creatorId: str
    recipientId: Optional[str]
    totalRedemptions: int
    redeemedAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
