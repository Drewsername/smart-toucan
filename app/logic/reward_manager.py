from fastapi import HTTPException
from app.logic.base_manager import BaseManager

class RewardManager(BaseManager):
    def __init__(self, user_id: int):
        super().__init__(user_id)
        self.reward = None

    async def load_reward(self, reward_id: int):
        self.reward = await self._prisma.reward.find_unique(where={"id": reward_id})
        if not self.reward:
            raise HTTPException(status_code=404, detail="Reward not found")

    async def get_total_points(self) -> int:
        tasks = await self._prisma.task.find_many(where={
            "userId": self.user_id, "completed": True
        })
        return sum(task.points for task in tasks)

    async def get_spent_points(self) -> int:
        redemptions = await self._prisma.redemption.find_many(
            where={"userId": self.user_id},
            include={"reward": True}
        )
        return sum(r.reward.cost for r in redemptions)

    async def redeem(self):
        await self.validate_user()
        await self.log_action("attempting_reward_redemption", {"reward_id": self.reward.id})
        total = await self.get_total_points()
        spent = await self.get_spent_points()
        if (total - spent) < self.reward.cost:
            raise HTTPException(status_code=400, detail="Not enough points")
        await self._prisma.redemption.create(data={
            "userId": self.user_id, "rewardId": self.reward.id
        })
        await self.log_action("reward_redeemed", {"reward_id": self.reward.id})
        return {"message": "Reward redeemed!"}
