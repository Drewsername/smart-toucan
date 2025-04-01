from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import HTTPException
from app.logic.base_manager import BaseManager
from app.schemas.task import TaskStatus

class TaskManager(BaseManager):

    async def create_task(self, data: dict) -> dict:
        profile = await self.get_user_or_403()

        if not profile.partnerId:
            raise HTTPException(status_code=400, detail="Cannot create a task without a partner")

        acceptance_deadline = (
            datetime.utcnow() + timedelta(minutes=data["acceptanceWindow"])
            if data.get("acceptanceWindow", 0) > 0 else None
        )

        new_task = await self._prisma.task.create(
            data={
                **data,
                "creatorId": self.user_id,
                "recipientId": profile.partnerId,
                "acceptanceDeadline": acceptance_deadline,
                "status": TaskStatus.pending.value
            }
        )

        await self.log_action("created_task", {"task_id": new_task.id})
        return self.serialize(new_task)


    async def update_task(self, task_id: str, data: dict) -> dict:
        await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.creatorId != self.user_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        updated = await self._prisma.task.update(
            where={"id": task_id},
            data=data
        )

        await self.log_action("updated_task", {"task_id": task_id})
        return self.serialize(updated)

    async def list_my_tasks(self) -> List[dict]:
        profile = await self.get_user_or_403()

        tasks = await self._prisma.task.find_many(
            where={
                "OR": [
                    {"creatorId": self.user_id},
                    {"recipientId": self.user_id}
                ]
            },
            take=100
        )

        # Filter tasks based on current partnership
        return [
            self.serialize(task)
            for task in tasks
            if (task.creatorId == self.user_id and task.recipientId == profile.partnerId) or
               (task.recipientId == self.user_id and task.creatorId == profile.partnerId)
        ]

    async def accept_task(self, task_id: str) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.recipientId != self.user_id or task.creatorId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")

        if task.status != TaskStatus.pending.value:
            raise HTTPException(status_code=400, detail="Task not in pending state")

        if task.acceptanceDeadline and datetime.now(timezone.utc) > task.acceptanceDeadline:
            await self._prisma.task.update(
                where={"id": task_id},
                data={"status": TaskStatus.expired.value}
            )
            raise HTTPException(status_code=400, detail="Acceptance window expired")

        updated = await self._prisma.task.update(
            where={"id": task_id},
            data={
                "status": TaskStatus.accepted.value,
                "acceptedAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
        )

        await self.log_action("accepted_task", {"task_id": task_id})
        return self.serialize(updated)

    async def decline_task(self, task_id: str) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.recipientId != self.user_id or task.creatorId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")

        if task.status != TaskStatus.pending.value:
            raise HTTPException(status_code=400, detail="Task not in pending state")

        if task.acceptanceDeadline and datetime.now(timezone.utc) > task.acceptanceDeadline:
            await self._prisma.task.update(
                where={"id": task_id},
                data={"status": TaskStatus.expired.value}
            )
            raise HTTPException(status_code=400, detail="Acceptance window expired")

        updated = await self._prisma.task.update(
            where={"id": task_id},
            data={
                "status": TaskStatus.declined.value,
                "updatedAt": datetime.now(timezone.utc)
            }
        )

        await self.log_action("declined_task", {"task_id": task_id})
        return self.serialize(updated)

    async def bid_on_task(self, task_id: str, bid_value: int) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.recipientId != self.user_id or task.creatorId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")

        if not task.isBiddable:
            raise HTTPException(status_code=400, detail="Task is not biddable")

        if task.status != TaskStatus.pending.value:
            raise HTTPException(status_code=400, detail="Task not in pending state")

        if task.acceptanceDeadline and datetime.utcnow() > task.acceptanceDeadline:
            await self._prisma.task.update(
                where={"id": task_id},
                data={"status": TaskStatus.expired.value}
            )
            raise HTTPException(status_code=400, detail="Acceptance window expired")

        reservation_price = task.reservationPrice or 0

        if bid_value <= reservation_price:
            updated = await self._prisma.task.update(
                where={"id": task_id},
                data={
                    "status": TaskStatus.accepted.value,
                    "acceptedAt": datetime.utcnow(),
                    "bidValue": bid_value
                }
            )
            await self.log_action("accepted_task_with_bid", {"task_id": task_id, "bid": bid_value})
        else:
            updated = await self._prisma.task.update(
                where={"id": task_id},
                data={
                    "status": TaskStatus.declined.value,
                    "declinedAt": datetime.utcnow(),
                    "bidValue": bid_value
                }
            )
            await self.log_action("declined_task_with_bid", {"task_id": task_id, "bid": bid_value})

        return self.serialize(updated)

    async def delete_task(self, task_id: str) -> dict:
        await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.creatorId != self.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this task")

        deleted = await self._prisma.task.delete(where={"id": task_id})
        await self.log_action("deleted_task", {"task_id": task_id})
        return self.serialize(deleted)


    async def complete_task(self, task_id: str) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if task.recipientId != self.user_id or task.creatorId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")

        if task.status != TaskStatus.accepted.value:
            raise HTTPException(status_code=400, detail="Task is not in accepted state")

        if task.hasTimeLimit and task.acceptedAt and task.timeLimit:
            deadline = task.acceptedAt + timedelta(minutes=task.timeLimit)
            if datetime.now(timezone.utc) > deadline:
                await self._prisma.task.update(
                    where={"id": task_id},
                    data={"status": TaskStatus.expired.value}
                )
                raise HTTPException(status_code=400, detail="Task time limit expired")

        updated = await self._prisma.task.update(
            where={"id": task_id},
            data={
                "status": TaskStatus.completed.value,
                "completedAt": datetime.now(timezone.utc),
                "updatedAt": datetime.now(timezone.utc)
            }
        )

        await self.log_action("completed_task", {"task_id": task_id})
        return self.serialize(updated)
        

    async def creator_validate_task(self, task_id: str) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.creatorId != self.user_id or task.recipientId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")
        if task.status != TaskStatus.completed.value:
            raise HTTPException(status_code=400, detail="Task must be marked complete first")

        await self.log_action("partner_validated_completion", {"task_id": task_id})
        return self.serialize(task)
        
    async def creator_force_complete(self, task_id: str) -> dict:
        profile = await self.get_user_or_403()

        task = await self._prisma.task.find_unique(where={"id": task_id})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.creatorId != self.user_id or task.recipientId != profile.partnerId:
            raise HTTPException(status_code=403, detail="Not authorized")
        if task.status in [TaskStatus.completed.value, TaskStatus.expired.value]:
            raise HTTPException(status_code=400, detail="Task already completed or expired")

        updated = await self._prisma.task.update(
            where={"id": task_id},
            data={"status": TaskStatus.completed.value, "completedAt": datetime.utcnow()}
        )
        await self.log_action("partner_forced_completion", {"task_id": task_id})
        return self.serialize(updated)

