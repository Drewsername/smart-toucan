import os
import httpx
import time
import logging
from fastapi import Request, HTTPException, Header
from app.core.db import prisma

logger = logging.getLogger(__name__)

# Cache user authentication results
_auth_cache = {}
_AUTH_CACHE_TIMEOUT = 300  # 5 minutes

async def get_current_user_id(request: Request) -> str:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise HTTPException(status_code=500, detail="Missing Supabase configuration")

    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")
    
    # Check if token is in cache
    cached = _auth_cache.get(token)
    now = time.time()
    
    if cached and (now - cached['timestamp'] < _AUTH_CACHE_TIMEOUT):
        return cached['user_id']

    # Token not in cache, validate with Supabase
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            res = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": SUPABASE_ANON_KEY,
                }
            )
        except httpx.TimeoutException:
            raise HTTPException(status_code=503, detail="Authentication service unavailable")

    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = res.json()
    user_id = user["id"]

    if "email" not in user:
        raise HTTPException(status_code=400, detail="Email is required")

    email = user.get("email")

    # Check if profile exists - without using select parameter
    profile = await prisma.profile.find_unique(where={"id": user_id})
    
    if not profile:
        # Create profile if it doesn't exist
        await prisma.profile.create(data={"id": user_id, "email": email})

    # Update cache
    _auth_cache[token] = {
        'user_id': user_id,
        'timestamp': now
    }
    
    # Cleanup old cache entries if cache is too large
    if len(_auth_cache) > 1000:
        # Remove oldest entries
        sorted_keys = sorted(_auth_cache.keys(), key=lambda k: _auth_cache[k]['timestamp'])
        for key in sorted_keys[:200]:  # Remove oldest 200 entries
            del _auth_cache[key]
    
    return user_id


def verify_cron_key(key: str = Header(...)):
    """Verify the cron job secret key"""
    if key != os.getenv("CRON_SECRET_KEY"):
        raise HTTPException(status_code=401, detail="Invalid cron key")
