from __future__ import annotations
from typing import Any
import httpx
from personality_core.adapters.base import ModelAdapter
from personality_core.config import OLLAMA_BASE_URL

class OllamaAdapter(ModelAdapter):
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def generate(self, model: str, messages: list[dict[str, Any]], temperature: float | None = None, max_tokens: int | None = None) -> str:
        ollama_model = model.split("/", 1)[1] if model.startswith("ollama/") else model
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        payload = {"model": ollama_model, "messages": messages, "stream": False, "options": options}
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
