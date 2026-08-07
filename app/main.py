from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.logging import LoggingMiddleware
from app.shared.database import get_db
from app.shared.logger import configure_logging, get_logger
from app.shared.redis import get_redis, init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

configure_logging()
logger = get_logger()

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

@app.get("/health")
async def health(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        db_ok = False

    # Check Redis
    try:
        await redis.ping()
        redis_ok = True
    except Exception as e:
        redis_ok = False

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "database": db_ok,
        "redis": redis_ok
    }