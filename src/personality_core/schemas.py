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
    fail_policy: Literal["warn", "repair", "block", "raw"] = "warn"
    repair: bool | None = None
    debug: bool = False
    temperature: float | None = None
    max_tokens: int | None = None
    think: bool | str | None = False
    stream: bool = False

class CompareRequest(BaseModel):
    model: str
    prompt: str
    personalities: list[str] = Field(default_factory=list)
    max_tokens: int | None = 300
    temperature: float | None = None
    think: bool | str | None = False
    stabilizer: StabilizerConfig | bool | None = None

class StackRequest(BaseModel):
    model: str = "ollama/gemma4:e4b"
    prompt: str = ""
    cores: list[CoreRef] = Field(default_factory=list)
    base_traits: dict[str, float] = Field(default_factory=dict)
    max_tokens: int | None = 300
    temperature: float | None = None
    think: bool | str | None = False
    stabilizer: StabilizerConfig | bool | None = None
    fail_policy: Literal["warn", "repair", "block", "raw"] = "warn"

class CoreDraftRequest(BaseModel):
    intent: str
    name: str | None = None
    author: str = "local"
    model: str | None = None
    max_tokens: int | None = 900
    temperature: float | None = 0.2
    think: bool | str | None = False

class CoreInstallRequest(BaseModel):
    core: dict[str, Any]
    overwrite: bool = False

class ProviderHealthRequest(BaseModel):
    model: str
    prompt: str = "Reply with OK."
    max_tokens: int | None = 24
    temperature: float | None = 0.0
    think: bool | str | None = False

class CoreDefinition(BaseModel):
    id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    author: str = "unknown"
    kind: str = "personality"
    trait_deltas: dict[str, float] = Field(default_factory=dict)
    default_strength: float = 0.5
    params: dict[str, Any] = Field(default_factory=dict)
    rules: list[str] = Field(default_factory=list)
    boundaries: dict[str, bool] = Field(default_factory=dict)
    evaluation_weights: dict[str, float] = Field(default_factory=dict)
    contracts: list[dict[str, Any]] = Field(default_factory=list)
    conflicts_with: list[dict[str, str]] = Field(default_factory=list)
    examples: list[dict[str, str]] = Field(default_factory=list)

class ResolvedStack(BaseModel):
    base_traits: dict[str, float] = Field(default_factory=dict)
    resolved_traits: dict[str, float] = Field(default_factory=dict)
    boundaries: dict[str, bool] = Field(default_factory=dict)
    rules: list[str] = Field(default_factory=list)
    contracts: list[dict[str, Any]] = Field(default_factory=list)
    active_cores: list[dict[str, Any]] = Field(default_factory=list)
    core_trace: list[dict[str, Any]] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
