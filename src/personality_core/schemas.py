from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field

class CoreRef(BaseModel):
    id: str
    strength: float | None = None
    params: dict[str, Any] = Field(default_factory=dict)

class StabilizerConfig(BaseModel):
    enabled: bool = False
    threshold: float = 0.78
    max_attempts: int = 1

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"] | str
    content: str | list[Any] | None = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    personality: str | None = None
    cores: list[CoreRef] = Field(default_factory=list)
    stabilizer: StabilizerConfig | bool | None = None
    repair: bool | None = None
    debug: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False

class CoreDefinition(BaseModel):
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = "unknown"
    trait_deltas: dict[str, float] = Field(default_factory=dict)
    default_strength: float = 0.5
    params: dict[str, Any] = Field(default_factory=dict)
    rules: list[str] = Field(default_factory=list)
    boundaries: dict[str, bool] = Field(default_factory=dict)
    evaluation_weights: dict[str, float] = Field(default_factory=dict)
    conflicts_with: list[dict[str, str]] = Field(default_factory=list)
    examples: list[dict[str, str]] = Field(default_factory=list)

class ResolvedStack(BaseModel):
    base_traits: dict[str, float] = Field(default_factory=dict)
    resolved_traits: dict[str, float] = Field(default_factory=dict)
    boundaries: dict[str, bool] = Field(default_factory=dict)
    rules: list[str] = Field(default_factory=list)
    active_cores: list[dict[str, Any]] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
