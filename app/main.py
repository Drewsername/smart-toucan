from fastapi import FastAPI
from app.core.db import connect_db, disconnect_db, prisma
from app.api.routes import reward_routes, health_routes, pairing_routes, task_routes
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio

logger = logging.getLogger(__name__)
app = FastAPI()

# Immediate warm-up helper
async def _immediate_warmup():
    logger.info("🚀 Running app warm-up")
    await connect_db()
    await prisma.profile.count()
    await prisma.pairingcode.count()
    from app.logic import base_manager, reward_manager, pairing_manager, health_manager
    logger.info("✅ Warm-up finished")

def run_warmup_safe():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        asyncio.create_task(_immediate_warmup())
    else:
        asyncio.run(_immediate_warmup())

run_warmup_safe()

# Add middleware and routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()

@app.get("/")
async def root():
    return {"message": "Toucan API is running!"}

app.include_router(reward_routes.router, prefix="/api")
app.include_router(health_routes.router, prefix="/api")
app.include_router(pairing_routes.router, prefix="/api")
app.include_router(task_routes.router, prefix="/api")