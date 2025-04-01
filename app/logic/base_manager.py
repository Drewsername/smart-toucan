import logging
import time
from fastapi import HTTPException
from app.core.db import prisma

logger = logging.getLogger(__name__)
_user_cache = {}
_CACHE_TIMEOUT = 300  # seconds

class BaseManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._prisma = prisma

    async def get_user_or_403(self, refresh: bool = False):
        cache_key = f"user_{self.user_id}"
        now = time.time()

        cached = _user_cache.get(cache_key)
        if cached and not refresh and now - cached['timestamp'] < _CACHE_TIMEOUT:
            return cached['user']

        user = await self._prisma.profile.find_unique(where={"id": self.user_id})
        if not user:
            raise HTTPException(status_code=403, detail="Unauthorized")

        _user_cache[cache_key] = {'user': user, 'timestamp': now}
        return user

    @staticmethod
    def invalidate_user_cache(user_id: str):
        """Manually evict a user from the cache by ID."""
        _user_cache.pop(f"user_{user_id}", None)


    def serialize(self, obj) -> dict:
        return obj.model_dump() if hasattr(obj, "model_dump") else dict(obj)

    def serialize_many(self, objs) -> list[dict]:
        return [self.serialize(o) for o in objs]

    def log(self, message: str, level: str = "info", meta: dict = None):
        log_fn = getattr(logger, level, None)
        if callable(log_fn):
            log_fn(message, extra=meta or {})
        else:
            logger.info(message, extra=meta or {})

    async def log_action(self, action: str, meta: dict = None, level: str = "info"):
        self.log(f"[user:{self.user_id}] {action}", level, meta)
