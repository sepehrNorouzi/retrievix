from typing import Optional, Dict, Any

import httpx

from app.ai.llm.base import LLMClient


class OllamaLLMClient(LLMClient):

    async def generate(
            self,
            prompt: str,
            system: Optional[str] = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a completion for the given prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=self.timeout.total_seconds()) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": options,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
