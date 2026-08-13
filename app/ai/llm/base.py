from abc import ABC
from datetime import timedelta
from typing import Optional, Dict, Any


class LLMClient(ABC):


    def __init__(self, base_url: str, model: str, timeout: timedelta = timedelta(seconds=60)):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def generate(
            self,
            prompt: str,
            system: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> str:
        ...

