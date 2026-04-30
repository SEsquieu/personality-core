from __future__ import annotations
from typing import Any
import httpx
from personality_core.adapters.base import ModelAdapter, ModelAdapterError, ModelResponse
from personality_core.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_TIMEOUT

class OpenAIAdapter(ModelAdapter):
    def __init__(self, api_key: str = OPENAI_API_KEY, base_url: str = OPENAI_BASE_URL, timeout: float = OPENAI_TIMEOUT, extra_headers: dict[str, str] | None = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.extra_headers = extra_headers or {}

    async def generate(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        think: bool | str | None = False,
    ) -> ModelResponse:
        provider, provider_model = split_provider_model(model, default_provider="openai")
        if provider_model == model and model.startswith("openai/"):
            provider_model = model.split("/", 1)[1]
        headers = {"Content-Type": "application/json", **self.extra_headers}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        elif provider == "openai":
            raise ModelAdapterError("OPENAI_API_KEY is not set. Add it to your environment or use an Ollama model.")
        payload: dict[str, Any] = {"model": provider_model, "messages": messages, "stream": False}
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                choice = (data.get("choices") or [{}])[0]
                content = choice.get("message", {}).get("content", "")
                if isinstance(content, list):
                    content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
                if not str(content).strip():
                    raise ModelAdapterError(f"{provider} returned an empty message for {provider_model}.")
                return ModelResponse(
                    content=str(content),
                    done_reason=choice.get("finish_reason"),
                    usage=data.get("usage"),
                )
        except httpx.ConnectError as exc:
            raise ModelAdapterError(f"Could not connect to {provider} at {self.base_url}.") from exc
        except httpx.ReadTimeout as exc:
            raise ModelAdapterError(f"{provider} timed out after {self.timeout:g}s while running {provider_model}.") from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text.strip()
            raise ModelAdapterError(f"{provider} returned HTTP {exc.response.status_code}: {detail}") from exc

def split_provider_model(model: str, default_provider: str) -> tuple[str, str]:
    if "/" not in model:
        return default_provider, model
    provider, provider_model = model.split("/", 1)
    return provider, provider_model
