from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import HTTPException, Depends
from app.logic.base_manager import BaseManager
from app.schemas.task import TaskStatus
from app.logic.notification_manager import NotificationManager
from app.schemas.notification import NotificationCreate
class TaskManager(BaseManager):
    def __init__(self, user_id: str):
        super().__init__(user_id)
        self.notification_manager = NotificationManager(user_id)

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
        # Notify recipient
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=profile.partnerId,
                    type="TASK_CREATED",
                    message=f"You received a new task: '{new_task.title}'"
                )
            )
        except Exception as e:
            # Log error, but don't block task creation
            print(f"Error creating notification for new task {new_task.id}: {e}") # Replace with proper logging
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
        # Notify creator
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=task.creatorId,
                    type="TASK_ACCEPTED",
                    message=f"Your partner accepted the task: '{task.title}'"
                )
            )
        except Exception as e:
            print(f"Error creating notification for accepted task {task.id}: {e}") # Replace with proper logging
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
        # Notify creator
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=task.creatorId,
                    type="TASK_DECLINED",
                    message=f"Your partner declined the task: '{task.title}'"
                )
            )
        except Exception as e:
            print(f"Error creating notification for declined task {task.id}: {e}") # Replace with proper logging
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
            # Notify creator
            try:
                await self.notification_manager.create_notification(
                    NotificationCreate(
                        userId=task.creatorId,
                        type="TASK_ACCEPTED",
                        message=f"Your partner accepted task '{task.title}' with a bid of {bid_value}."
                    )
                )
            except Exception as e:
                print(f"Error creating notification for accepted bid task {task.id}: {e}") # Replace with proper logging
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
            # Notify creator
            try:
                await self.notification_manager.create_notification(
                    NotificationCreate(
                        userId=task.creatorId,
                        type="TASK_DECLINED",
                        message=f"Your partner declined task '{task.title}' with a bid of {bid_value}."
                    )
                )
            except Exception as e:
                print(f"Error creating notification for declined bid task {task.id}: {e}") # Replace with proper logging

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
        # Notify creator
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=task.creatorId,
                    type="TASK_COMPLETED",
                    message=f"Your partner marked task '{task.title}' as complete."
                )
            )
        except Exception as e:
            print(f"Error creating notification for completed task {task.id}: {e}") # Replace with proper logging
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
        # Notify recipient
        try:
            await self.notification_manager.create_notification(
                NotificationCreate(
                    userId=task.recipientId,
                    type="TASK_COMPLETED",
                    message=f"Your partner marked task '{task.title}' as complete (forced)."
                )
            )
        except Exception as e:
            print(f"Error creating notification for force completed task {task.id}: {e}") # Replace with proper logging
        return self.serialize(updated)
    async def find_expired_tasks(self) -> list:
        """Find tasks past their deadline"""
        now = datetime.now(timezone.utc)
        return await self._prisma.task.find_many(
            where={
                "status": "PENDING",
                "acceptanceDeadline": {"lt": now}
            }
        )

    async def mark_task_expired(self, task_id: str) -> dict:
        """Mark task as expired"""
        updated = await self._prisma.task.update(
            where={"id": task_id},
            data={"status": "EXPIRED"}
        )
        await self.log_action("marked_task_expired", {"task_id": task_id})
        return self.serialize(updated)


