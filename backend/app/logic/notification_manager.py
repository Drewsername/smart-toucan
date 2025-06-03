import logging
from typing import List, Optional

from prisma import Prisma
from prisma.models import Notification as PrismaNotification

from app.logic.base_manager import BaseManager
from app.schemas.notification import Notification, NotificationCreate

logger = logging.getLogger(__name__)


class NotificationManager(BaseManager):
    """Manages notification-related operations."""

    def __init__(self, user_id: str):
        """
        Initializes the NotificationManager.

        Args:
            user_id: The ID of the user associated with this manager instance.
        """
        super().__init__(user_id)
        # self._prisma is initialized in BaseManager

    async def create_notification(self, notification_data: NotificationCreate) -> Notification:
        """
        Creates a new notification in the database.

        Args:
            notification_data: The data for the notification to create including:
                - userId: Recipient user ID
                - type: Notification type
                - message: Notification content
                - referenceLink: Optional relative URL to referenced resource

        Returns:
            The created notification Pydantic model.
        """
        self.log(f"Creating notification for user {notification_data.userId}")
        notification_dict = notification_data.model_dump()
        if notification_dict.get('referenceLink') is None:
            notification_dict.pop('referenceLink', None)
            
        created_notification: PrismaNotification = await self._prisma.notification.create(
            data=notification_dict
        )
        self.log(f"Notification {created_notification.id} created successfully.")
        return Notification.model_validate(created_notification)

    async def get_notifications_for_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """
        Retrieves a list of notifications for a specific user, ordered by creation date.

        Args:
            user_id: The ID of the user whose notifications to retrieve.
            skip: The number of notifications to skip (for pagination).
            limit: The maximum number of notifications to return (for pagination).

        Returns:
            A list of notification Pydantic models.
        """
        self.log(f"Fetching notifications for user {user_id} (skip={skip}, limit={limit})")
        notifications: List[PrismaNotification] = await self._prisma.notification.find_many(
            where={"userId": user_id},
            order={"createdAt": "desc"},
            skip=skip,
            take=limit,
        )
        self.log(f"Found {len(notifications)} notifications for user {user_id}.")
        return [Notification.model_validate(n) for n in notifications]

    async def mark_notification_as_read(
        self, notification_id: int, user_id: int
    ) -> Optional[Notification]:
        """
        Marks a specific notification as read for a given user.

        Ensures the notification belongs to the user before updating.

        Args:
            notification_id: The ID of the notification to mark as read.
            user_id: The ID of the user who owns the notification.

        Returns:
            The updated notification Pydantic model, or None if not found or
            not owned by the user.
        """
        self.log(f"Attempting to mark notification {notification_id} as read for user {user_id}")
        # We use update_many with a where clause to ensure atomicity and ownership check
        updated_count = await self._prisma.notification.update_many(
            where={"id": notification_id, "userId": user_id, "isRead": False},
            data={"isRead": True},
        )

        if updated_count > 0:
            self.log(f"Notification {notification_id} marked as read for user {user_id}")
            # Fetch the updated notification to return it
            updated_notification = await self._prisma.notification.find_unique(
                where={"id": notification_id}
            )
            if updated_notification:
                 return Notification.model_validate(updated_notification)
            else:
                # Should not happen if update_many succeeded, but handle defensively
                logger.error(f"Failed to fetch notification {notification_id} after successful update_many.")
                return None
        else:
            # Check if it exists but wasn't updated (e.g., already read or wrong user)
            existing = await self._prisma.notification.find_first(
                where={"id": notification_id}
            )
            if not existing:
                self.log(f"Notification {notification_id} not found.", level="warning")
            elif existing.userId != user_id:
                 self.log(f"Notification {notification_id} does not belong to user {user_id}.", level="warning")
            elif existing.isRead:
                 self.log(f"Notification {notification_id} was already marked as read.", level="info")
            else:
                 # Should not happen given the update_many logic
                 logger.error(f"Inconsistent state for notification {notification_id} during mark as read.")

            return None


    async def mark_all_notifications_as_read(self, user_id: int) -> int:
        """
        Marks all unread notifications for a specific user as read.

        Args:
            user_id: The ID of the user whose notifications to mark as read.

        Returns:
            The count of notifications that were updated.
        """
        self.log(f"Marking all unread notifications as read for user {user_id}")
        result = await self._prisma.notification.update_many(
            where={"userId": user_id, "isRead": False}, data={"isRead": True}
        )
        count = result if isinstance(result, int) else 0 # update_many returns count
        self.log(f"Marked {count} notifications as read for user {user_id}.")
    async def create_task_expired_notification(self, task) -> Optional[Notification]:
        """
        Creates a notification for an expired task.

        Args:
            task: The expired task object
        
        Returns:
            The created notification if successful, None otherwise
        """
        try:
            notification = await self.create_notification(
                NotificationCreate(
                    userId=task.creatorId,
                    type="TASK_EXPIRED",
                    message=f"Task '{task.title}' has expired",
                    referenceLink=f"/tasks/{task.id}"
                )
            )
            self.log(f"Created expiration notification for task {task.id}")
            return notification
        except Exception as e:
            logger.error(f"Failed to create task expired notification: {e}")
            return None
