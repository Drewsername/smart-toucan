import os
import time
from app.core.db import check_db_health

SERVER_START_TIME = time.time()

class HealthCheckManager:
    async def check_database(self) -> dict:
        return await check_db_health()

    def get_uptime(self) -> str:
        uptime_seconds = int(time.time() - SERVER_START_TIME)
        hours, remainder = divmod(uptime_seconds, 3600)
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
            "status": "ok" if db_status.get("database") == "connected" else "error",
            "services": db_status,
            "uptime": self.get_uptime(),
            "meta": self.get_metadata(),
        }
