from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProvider(ABC):

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        ...

    @abstractmethod
    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        ...

    @abstractmethod
    async def health(self) -> Dict[Any, Any]:
        ...
