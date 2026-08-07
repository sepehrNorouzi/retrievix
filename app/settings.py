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


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = Extra.allow


settings = Settings()
