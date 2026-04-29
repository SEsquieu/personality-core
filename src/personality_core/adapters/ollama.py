from __future__ import annotations
from typing import Any
import httpx
from personality_core.adapters.base import ModelAdapter, ModelAdapterError, ModelResponse
from personality_core.config import OLLAMA_BASE_URL, OLLAMA_TIMEOUT

class OllamaAdapter(ModelAdapter):
    def __init__(self, base_url: str = OLLAMA_BASE_URL, timeout: float = OLLAMA_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> ModelResponse:
        ollama_model = model.split("/", 1)[1] if model.startswith("ollama/") else model
        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        payload = {"model": ollama_model, "messages": messages, "stream": False, "options": options}
        if think is not None:
            payload["think"] = think
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                if not content.strip():
                    reason = data.get("done_reason") or data.get("done")
                    thinking = data.get("message", {}).get("thinking")
                    thinking_note = " The model returned thinking text but no visible answer." if thinking else ""
                    raise ModelAdapterError(
                        f"Ollama returned an empty message for {ollama_model}. done={reason!r}. "
                        f"think={think!r}.{thinking_note} "
                        "Try --think false, a larger --max-tokens value, a different chat model, or run the command again after the model finishes loading."
                    )
                usage = {
                    "prompt_eval_count": data.get("prompt_eval_count"),
                    "eval_count": data.get("eval_count"),
                    "total_duration": data.get("total_duration"),
                }
                return ModelResponse(content=content, done_reason=data.get("done_reason"), usage=usage)
        except httpx.ConnectError as exc:
            raise ModelAdapterError(
                f"Could not connect to Ollama at {self.base_url}. Start Ollama or pass --model for another supported backend."
            ) from exc
        except httpx.ReadTimeout as exc:
            raise ModelAdapterError(
                f"Ollama timed out after {self.timeout:g}s while running {ollama_model}. Try --max-tokens 120, a smaller model, or OLLAMA_TIMEOUT=600."
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip()
            raise ModelAdapterError(f"Ollama returned HTTP {exc.response.status_code}: {detail}") from exc
