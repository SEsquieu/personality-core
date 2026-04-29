from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(self, model: str, messages: list[dict[str, Any]], temperature: float | None = None, max_tokens: int | None = None) -> str:
        raise NotImplementedError
