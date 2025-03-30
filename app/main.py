from fastapi import FastAPI
from app.core.db import connect_db, disconnect_db
from app.api.routes import reward_routes, health_routes


app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()

@app.get("/")
async def root():
    return {"message": "Toucan API is running!"}


app.include_router(reward_routes.router, prefix="/api")
app.include_router(health_routes.router, prefix="/api")
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
