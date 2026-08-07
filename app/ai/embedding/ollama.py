import asyncio
import httpx
from typing import List, Dict, Any
from app.ai.embedding.base import EmbeddingProvider
from app.settings import settings

class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str = None,
        timeout: float = 30.0,
        max_concurrent: int = 10,
    ):
        self.model = model
        self.base_url = (base_url or settings.ollama_url).rstrip("/")
        self.timeout = timeout
        self.max_concurrent = max_concurrent

    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts concurrently.
        Uses a semaphore to limit concurrency.
        """
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def embed_one(text: str) -> List[float]:
            async with semaphore:
                return await self.embed(text)

        tasks = [embed_one(text) for text in texts]
        return await asyncio.gather(*tasks)

    async def health(self) -> Dict[Any, Any]:
        """
        Check if Ollama is reachable and the required model is available.
        Returns a dict with status and details.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # 1. Check if Ollama API is responding
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()

                # 2. Check if our model exists in the list
                models = [model["name"] for model in data.get("models", [])]
                model_available = any(self.model in name for name in models)

                if model_available:
                    return {
                        "ok": True,
                        "status": "healthy",
                        "model": self.model,
                        "available_models": models,
                    }
                else:
                    return {
                        "ok": False,
                        "status": "unhealthy",
                        "error": f"Model '{self.model}' not found in Ollama",
                        "available_models": models,
                    }

        except httpx.ConnectError:
            return {
                "ok": False,
                "status": "unhealthy",
                "error": f"Could not connect to Ollama at {self.base_url}",
            }
        except Exception as e:
            return {
                "ok": False,
                "status": "unhealthy",
                "error": f"Unexpected error: {str(e)}",
            }