import os
import httpx
from fastapi import Request, HTTPException
from app.core.db import prisma  # Assuming you're using prisma-client-py


async def get_current_user_id(request: Request) -> str:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    if not SUPABASE_URL:
        raise HTTPException(status_code=500, detail="SUPABASE_URL environment variable is not set")
    if not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="SUPABASE_ANON_KEY environment variable is not set")

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")

    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_ANON_KEY,
            }
        )

    print("Supabase response:", res.status_code, res.text)

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = res.json()
    user_id = user["id"]

    if "email" not in user:
        raise HTTPException(status_code=400, detail="Email is required")

    email = user.get("email")

    # Ensure a Profile exists in your DB
    profile = await prisma.profile.find_unique(where={"id": user_id})
    if not profile:
        await prisma.profile.create(data={"id": user_id, "email": email})

    return user_id
