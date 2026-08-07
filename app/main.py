from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from qdrant_client import AsyncQdrantClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embedding import get_embedding_provider, EmbeddingProvider
from app.middleware.logging import LoggingMiddleware
from app.shared.database import get_db
from app.shared.logger import configure_logging, get_logger
from app.shared.qdrant import init_qdrant, close_qdrant, get_qdrant
from app.shared.redis import get_redis, init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()
    await init_qdrant()
    yield
    # Shutdown
    await close_qdrant()
    await close_redis()

configure_logging()
logger = get_logger()

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggingMiddleware)

@app.get("/health")
async def health(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
    qdrant: AsyncQdrantClient = Depends(get_qdrant),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
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

    try:
        await qdrant.get_collections()
        qdrant_ok = True
    except Exception:
        qdrant_ok = False

    embedding_provider_health = await embedding_provider.health()
    embedding_provider_ok = embedding_provider_health.get("ok", False)

    ok = all([db_ok, redis_ok, qdrant_ok, embedding_provider_ok])

    return {
        "status": "ok" if ok else "degraded",
        "database": db_ok,
        "redis": redis_ok,
        "qdrant": qdrant_ok,
        "embedding_provider": embedding_provider_ok,
    }