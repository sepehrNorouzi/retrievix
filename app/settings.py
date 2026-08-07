from pydantic.v1 import Extra
from pydantic_settings import BaseSettings
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    redis_host: str = os.environ.get("REDIS_HOST", "localhost")
    redis_port: int = os.environ.get("REDIS_PORT", 6379)
    redis_password: Optional[str] = os.environ.get("REDIS_PASSWORD", None)
    redis_db: int = os.environ.get("REDIS_DB", 0)

    debug: bool = os.environ.get("DEBUG", '0') in ["1", "true", "True"]
    api_keys: Dict[str, str] = {"some_key": "some_value"}

    DATABASE_URL: str = os.environ.get("DATABASE_URL")

    qdrant_host: str = os.environ.get("QDRANT_HOST", "localhost")
    qdrant_grpc_port: int = int(os.environ.get("QDRANT_GRPC_PORT", "6334"))
    qdrant_api_key: Optional[str] = os.environ.get("QDRANT_API_KEY", None)
    qdrant_init_collection: str = os.environ.get("QDRANT_INIT_COLLECTION", "retrievix")
    qdrant_vector_size: int = int(os.environ.get("QDRANT_VECTOR_SIZE", "768"))
    qdrant_collection: str = os.environ.get("QDRANT_COLLECTION", "retrievix")

    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", None)
    ollama_model: str = os.environ.get("OLLAMA_MODEL", 'nomic-embed-text')

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = Extra.allow


settings = Settings()
