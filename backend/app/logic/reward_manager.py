from datetime import datetime
from typing import List
from fastapi import HTTPException, Depends
from app.logic.base_manager import BaseManager
from app.logic.notification_manager import NotificationManager
from app.schemas.notification import NotificationCreate
class RewardManager(BaseManager):
    def __init__(self, user_id: str):
        super().__init__(user_id)
        self.notification_manager = NotificationManager(user_id)

    async def create_reward(self, reward_data: dict) -> dict:
        user = await self.get_user_or_403(refresh=True)
        if not user.partnerId:
            raise HTTPException(status_code=400, detail="You must be paired to create rewards.")

        reward_data["creatorId"] = self.user_id
        reward_data["recipientId"] = user.partnerId

        created = await self._prisma.reward.create(
            data=reward_data,
            include={"creator": True, "recipient": True, "redemptions": True}
        )
        await self.log_action("created_reward", {"reward_id": created.id})
        # Notify recipient
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=user.partnerId,
                    type="NEW_REWARD",
                    message=f"Your partner created a new reward: '{created.title}'"
                )
            )
        except Exception as e:
            print(f"Error creating notification for new reward {created.id}: {e}") # Replace with proper logging
        return self.serialize(created)

    async def update_reward(self, reward_id: str, data: dict) -> dict:
        await self.get_user_or_403()
        try:
            updated = await self._prisma.reward.update(
                where={"id_creatorId": {"id": reward_id, "creatorId": self.user_id}},
                data=data,
                include={"creator": True, "recipient": True}
            )
            await self.log_action("updated_reward", {"reward_id": reward_id})
            return self.serialize(updated)
        except Exception as e:
            if "Record to update not found" in str(e):
                raise HTTPException(status_code=404, detail="Reward not found or not authorized")
            raise

    async def delete_reward(self, reward_id: str) -> dict:
        await self.get_user_or_403()
        reward = await self._prisma.reward.find_unique(where={"id": reward_id})
        if not reward or reward.creatorId != self.user_id:
            raise HTTPException(status_code=404, detail="Reward not found or not authorized")

        deleted = await self._prisma.reward.delete(where={"id": reward_id})
        await self.log_action("deleted_reward", {"reward_id": reward_id})
        return self.serialize(deleted)

    async def get_reward_by_id(self, reward_id: str) -> dict:
        user = await self.get_user_or_403()
        reward = await self._prisma.reward.find_first(
            where={
                "id": reward_id,
                "OR": [
                    {"creatorId": self.user_id},
                    {"recipientId": self.user_id}
                ]
            },
            include={"creator": True, "recipient": True, "redemptions": True}
        )
        if not reward:
            raise HTTPException(status_code=404, detail="Reward not found or not authorized")
        if reward.creatorId != self.user_id and reward.recipientId != user.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")
        return self.serialize(reward)

    async def list_rewards_for_user(self) -> List[dict]:
        user = await self.get_user_or_403()
        rewards = await self._prisma.reward.find_many(
            where={
                "OR": [
                    {"creatorId": self.user_id},
                    {"recipientId": self.user_id}
                ]
            },
            include={"creator": True, "recipient": True, "redemptions": True},
            take=50
        )
        return [r for r in self.serialize_many(rewards) if r["creatorId"] == self.user_id or r["recipientId"] == user.partnerId]

    async def list_rewards_for_partner(self) -> List[dict]:
        user = await self.get_user_or_403()
        rewards = await self._prisma.reward.find_many(
            where={"recipientId": self.user_id},
            include={"creator": True, "recipient": True, "redemptions": True},
            take=50
        )
        return [r for r in self.serialize_many(rewards) if r["creatorId"] == user.partnerId]

    async def redeem_reward(self, reward_id: str) -> dict:
        user = await self.get_user_or_403()
        async with self._prisma.tx() as tx:
            reward = await tx.reward.find_unique(
                where={"id": reward_id},
                include={"redemptions": True}
            )
            if not reward:
                raise HTTPException(status_code=404, detail="Reward not found")
            if reward.recipientId != self.user_id:
                raise HTTPException(status_code=403, detail="Not authorized")
            if reward.creatorId != user.partnerId:
                raise HTTPException(status_code=403, detail="You are not currently paired to the reward creator")

            if not reward.isUnlimited:
                today = datetime.now().date()
                redemptions_today = sum(
                    r.createdAt.date() == today for r in reward.redemptions
                )
                if reward.dailyLimit and redemptions_today >= reward.dailyLimit:
                    raise HTTPException(status_code=400, detail="Daily redemption limit reached")

            redemption = await tx.redemption.create(
                data={"userId": self.user_id, "rewardId": reward_id}
            )

            updated = await tx.reward.update(
                where={"id": reward_id},
                data={
                    "totalRedemptions": reward.totalRedemptions + 1,
                    "redeemedAt": datetime.now()
                },
                include={"creator": True, "recipient": True, "redemptions": True}
            )

        await self.log_action("redeemed_reward", {
            "reward_id": reward_id,
            "redemption_id": redemption.id
        })
        # Notify creator
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=reward.creatorId,
                    type="REWARD_REDEEMED",
                    message=f"Your partner redeemed the reward: '{reward.title}'"
                )
            )
        except Exception as e:
            print(f"Error creating notification for redeemed reward {reward.id}: {e}") # Replace with proper logging
        return self.serialize(updated)
