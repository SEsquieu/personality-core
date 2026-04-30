from __future__ import annotations
from pathlib import Path
from personality_core.schemas import ChatCompletionRequest, CoreRef
from personality_core.core.core_registry import CoreRegistry
from personality_core.core.core_stack import CoreStackResolver
from personality_core.core.persona_store import PersonaStore
from personality_core.core.mode_detector import detect_mode
from personality_core.core.compiler import CoreCompiler
from personality_core.scoring.heuristic import score_text
from personality_core.core.stabilizer import Stabilizer
from personality_core.adapters.ollama import OllamaAdapter
from personality_core.adapters.openai import OpenAIAdapter
from personality_core.config import (
    LM_STUDIO_BASE_URL,
    OPENROUTER_API_KEY,
    OPENROUTER_APP_NAME,
    OPENROUTER_BASE_URL,
    OPENROUTER_SITE_URL,
    OPENAI_BASE_URL,
)

class PersonalityPipeline:
    def __init__(self, cores_dir: Path, personalities_dir: Path, model_profiles_dir: Path):
        self.registry = CoreRegistry(cores_dir)
        self.personas = PersonaStore(personalities_dir)
        self.resolver = CoreStackResolver(self.registry)
        self.compiler = CoreCompiler(model_profiles_dir)
        self.stabilizer = Stabilizer()
        self.ollama = OllamaAdapter()
        self.openai = OpenAIAdapter()
        openrouter_headers = {}
        if OPENROUTER_SITE_URL:
            openrouter_headers["HTTP-Referer"] = OPENROUTER_SITE_URL
        if OPENROUTER_APP_NAME:
            openrouter_headers["X-Title"] = OPENROUTER_APP_NAME
        self.openrouter = OpenAIAdapter(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL, extra_headers=openrouter_headers)
        self.lmstudio = OpenAIAdapter(api_key="", base_url=LM_STUDIO_BASE_URL)

    def adapter_for(self, model: str):
        if model.startswith("ollama/") or "/" not in model:
            return self.ollama
        if model.startswith("openrouter/"):
            return self.openrouter
        if model.startswith("lmstudio/") or model.startswith("lm-studio/"):
            return self.lmstudio
        if model.startswith("openai/") or OPENAI_BASE_URL:
            return self.openai
        return self.openai

    async def run(self, req: ChatCompletionRequest) -> dict:
        base_traits, preset_cores, _preset = self.personas.load(req.personality)
        requested = req.cores or []
        core_refs: list[CoreRef] = requested if requested else preset_cores
        messages = [m.model_dump() for m in req.messages]
        mode = detect_mode(messages)
        resolved = self.resolver.resolve(core_refs, base_traits=base_traits)
        system_prompt = self.compiler.compile(resolved, mode=mode, model=req.model)
        outbound = [{"role": "system", "content": system_prompt}] + messages
        adapter = self.adapter_for(req.model)
        raw_response = await adapter.generate(req.model, outbound, temperature=req.temperature, max_tokens=req.max_tokens, think=req.think)
        raw = raw_response.content
        evaluation = score_text(raw, resolved)
        stabilizer_cfg = req.stabilizer
        enabled = bool(req.repair)
        threshold = 0.78
        if isinstance(stabilizer_cfg, bool):
            enabled = stabilizer_cfg
        elif stabilizer_cfg is not None:
            enabled = stabilizer_cfg.enabled
            threshold = stabilizer_cfg.threshold
        final = raw
        repaired = False
        if enabled and evaluation["core_match"] < threshold:
            repair_messages = self.stabilizer.build_repair_messages(messages, raw, resolved, evaluation)
            try:
                repair_response = await adapter.generate(req.model, repair_messages, temperature=0.2, max_tokens=req.max_tokens, think=req.think)
                final = repair_response.content
                repaired = True
                evaluation = score_text(final, resolved)
            except Exception:
                final = raw
        warnings = []
        if raw_response.done_reason == "length":
            warnings.append("Model output stopped because it hit max_tokens. Increase --max-tokens for a complete answer.")
        return {
            "content": final,
            "raw_content": raw,
            "repaired": repaired,
            "warnings": warnings,
            "debug": {
                "mode": mode,
                "resolved": resolved.model_dump(),
                "compiled_prompt": system_prompt,
                "evaluation": evaluation,
                "model_response": {"done_reason": raw_response.done_reason, "usage": raw_response.usage},
                "warnings": warnings,
            },
        }
