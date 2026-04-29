from __future__ import annotations
from typing import Any
from personality_core.adapters.base import ModelAdapter

class OpenAIAdapter(ModelAdapter):
    async def generate(self, model: str, messages: list[dict[str, Any]], temperature: float | None = None, max_tokens: int | None = None) -> str:
        raise NotImplementedError("OpenAI adapter placeholder. Use Ollama for the MVP or implement your provider call here.")
