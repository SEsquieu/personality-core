from __future__ import annotations
from typing import Any
from personality_core.adapters.base import ModelAdapter, ModelAdapterError, ModelResponse

class OpenAIAdapter(ModelAdapter):
    async def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> ModelResponse:
        raise ModelAdapterError(
            f"No adapter is implemented for model {model!r}. Use an Ollama model such as 'ollama/gemma4:e4b' "
            "or a bare local Ollama model name such as 'gemma4:e4b'."
        )
