import re
from abc import ABC, abstractmethod

from fastapi import UploadFile


class TextExtractorBase(ABC):

    @abstractmethod
    async def extract(self, content: bytes) -> str:
        ...

    def clean_text(self, text: str) -> str:
        """Normalize whitespace, remove excessive newlines, and trim."""
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(lines)
