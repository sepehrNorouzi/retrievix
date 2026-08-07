# app/services/redis_client.py
from typing import Optional
import redis.asyncio as redis
from app.settings import settings

_redis_client: Optional[redis.Redis] = None

async def init_redis() -> None:
    """Call this during FastAPI startup."""
    global _redis_client
    _redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True,
        max_connections=20,
    )

async def close_redis() -> None:
    """Call this during FastAPI shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

async def get_redis() -> redis.Redis:
    """FastAPI dependency that provides the Redis client."""
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Did you call init_redis()?")
    return _redis_client