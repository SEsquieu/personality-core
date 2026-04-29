from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

class ModelAdapterError(RuntimeError):
    pass

@dataclass(frozen=True)
class ModelResponse:
    content: str
    done_reason: str | None = None
    usage: dict[str, Any] | None = None

class ModelAdapter(ABC):
    @abstractmethod
    async def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> ModelResponse:
        raise NotImplementedError
