from .base import EmbeddingProvider
from .ollama import OllamaEmbeddingProvider

def get_embedding_provider() -> EmbeddingProvider:
    match settings.embedding_provider:
        case "ollama":
            return OllamaEmbeddingProvider(base_url=settings.ollama_base_url, model=settings.ollama_model)
        case _:
            raise ValueError("Unknown embedding provider")