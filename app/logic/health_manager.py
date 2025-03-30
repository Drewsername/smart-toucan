# app/logic/health_manager.py
import os
import time
from app.core.db import prisma

SERVER_START_TIME = time.time()

class HealthCheckManager:
    def __init__(self):
        self._prisma = prisma

    async def check_database(self) -> dict:
        try:
            await self._prisma.execute_raw("SELECT 1;")
            return {"database": "connected"}
        except Exception as e:
            return {"database": "disconnected", "error": str(e)}

    def get_uptime(self) -> str:
        seconds = int(time.time() - SERVER_START_TIME)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def get_metadata(self) -> dict:
        return {
            "version": os.getenv("TOUCAN_VERSION", "dev"),
            "env": os.getenv("ENV", "local"),
        }

    async def get_health_report(self) -> dict:
        db_status = await self.check_database()
        return {
            "status": "ok" if db_status["database"] == "connected" else "error",
            "services": db_status,
            "uptime": self.get_uptime(),
            "meta": self.get_metadata()
        }
