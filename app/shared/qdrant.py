from typing import Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import VectorParams, Distance

from app.settings import settings

_qdrant_client: Optional[AsyncQdrantClient] = None

async def init_qdrant() -> None:
    """Initialize the Qdrant client on application startup."""
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = AsyncQdrantClient(
            host=settings.qdrant_host,
            grpc_port=settings.qdrant_grpc_port,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False,
            timeout=10,
        )
        collections = await _qdrant_client.get_collections()
        collection_names = [getattr(c, "name", "") for c in collections.collections]
        if settings.qdrant_init_collection not in collection_names:
            await _qdrant_client.create_collection(
                collection_name=settings.qdrant_init_collection,
                vectors_config=VectorParams(size=settings.qdrant_vector_size, distance=Distance.COSINE,),
            )

async def close_qdrant() -> None:
    """Gracefully close the Qdrant client on shutdown."""
    global _qdrant_client
    if _qdrant_client is not None:
        await _qdrant_client.close()
        _qdrant_client = None

async def get_qdrant() -> AsyncQdrantClient:
    """FastAPI dependency that provides the Qdrant client."""
    if _qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call init_qdrant() first.")
    return _qdrant_client