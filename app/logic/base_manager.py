import logging
from fastapi import HTTPException
from app.core.db import prisma

logger = logging.getLogger(__name__)

class BaseManager:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._prisma = prisma

    async def validate_user(self):
        user = await self._prisma.user.find_unique(where={"id": self.user_id})
        if not user:
            raise HTTPException(status_code=403, detail="Unauthorized user")

    async def log_action(self, action: str, meta: dict = None):
        logger.info(f"[user:{self.user_id}] {action}", extra=meta or {})
