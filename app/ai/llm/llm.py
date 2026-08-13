from app.ai.llm.base import LLMClient
from app.ai.llm.llama3_2 import OllamaLLMClient
from app.settings import settings


def get_llm_client() -> LLMClient:
    match settings.llm_client:
        case "ollama":
            return OllamaLLMClient(base_url=settings.ollama_llm_base_url, model=settings.ollama_llm_model)
        case _:
            raise ValueError("Unknown embedding provider")