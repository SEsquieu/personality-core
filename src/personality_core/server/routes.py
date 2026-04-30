from __future__ import annotations
import json
from pathlib import Path
import re
from fastapi import APIRouter, HTTPException
from personality_core.adapters.base import ModelAdapterError
from personality_core.schemas import ChatCompletionRequest, ChatMessage, CompareRequest, CoreDraftRequest, CoreInstallRequest, StackRequest
from personality_core.core.mode_detector import detect_mode
from personality_core.core.pipeline import PersonalityPipeline
from personality_core.config import DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR
from personality_core.server.openai_compat import chat_completion_response

router = APIRouter()
pipeline = PersonalityPipeline(DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR)

@router.get("/health")
def health():
    return {"ok": True, "service": "personality-core"}

@router.get("/v1/cores")
def list_cores():
    return {"data": [c.model_dump() for c in pipeline.registry.list()]}

@router.get("/v1/cores/template")
def core_template():
    return {"core": build_core_template().model_dump()}

@router.post("/v1/cores/draft")
async def draft_core(req: CoreDraftRequest):
    warnings = []
    source = "deterministic"
    if req.model:
        try:
            core = await build_model_core_draft(req)
            source = "model"
        except ModelAdapterError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ValueError as exc:
            warnings.append(f"Model draft was invalid, so a deterministic draft was used instead: {exc}")
            core = build_core_draft(req)
    else:
        core = build_core_draft(req)
    return {"core": core.model_dump(), "source": source, "warnings": warnings}

@router.post("/v1/cores/validate")
def validate_core(req: CoreInstallRequest):
    try:
        core = pipeline.registry.validate_definition(req.core, source="request")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"valid": True, "core": core.model_dump(), "warnings": []}

@router.post("/v1/cores/install")
def install_core(req: CoreInstallRequest):
    try:
        core = pipeline.registry.install(req.core, overwrite=req.overwrite)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"installed": True, "core": core.model_dump()}

@router.get("/v1/personalities")
def list_personalities():
    return {"data": pipeline.personas.list()}

@router.post("/v1/run")
async def run(req: ChatCompletionRequest):
    try:
        return await pipeline.run(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/v1/compare")
async def compare(req: CompareRequest):
    selected = req.personalities or [p["id"] for p in pipeline.personas.list()]
    results = []
    for persona_id in selected:
        run_req = ChatCompletionRequest(
            model=req.model,
            messages=[ChatMessage(role="user", content=req.prompt)],
            personality=persona_id,
            stabilizer=req.stabilizer,
            debug=True,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            think=req.think,
        )
        try:
            result = await pipeline.run(run_req)
        except KeyError as exc:
            results.append({"personality": persona_id, "error": str(exc)})
            continue
        except ModelAdapterError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        results.append({"personality": persona_id, **result})
    return {"model": req.model, "prompt": req.prompt, "results": results}

@router.post("/v1/stack/resolve")
def resolve_stack(req: StackRequest):
    try:
        resolved = pipeline.resolver.resolve(req.cores, base_traits=req.base_traits)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"resolved": resolved.model_dump()}

@router.post("/v1/stack/compile")
def compile_stack(req: StackRequest):
    try:
        messages = [{"role": "user", "content": req.prompt}]
        mode = detect_mode(messages)
        resolved = pipeline.resolver.resolve(req.cores, base_traits=req.base_traits)
        compiled_prompt = pipeline.compiler.compile(resolved, mode=mode, model=req.model)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"mode": mode, "resolved": resolved.model_dump(), "compiled_prompt": compiled_prompt}

@router.post("/v1/stack/run")
async def run_stack(req: StackRequest):
    run_req = ChatCompletionRequest(
        model=req.model,
        messages=[ChatMessage(role="user", content=req.prompt)],
        cores=req.cores,
        stabilizer=req.stabilizer,
        debug=True,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        think=req.think,
    )
    try:
        return await pipeline.run(run_req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/v1/chat/completions")
async def chat(req: ChatCompletionRequest):
    if req.stream:
        raise HTTPException(status_code=400, detail="Streaming is not implemented in this MVP.")
    try:
        result = await pipeline.run(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ModelAdapterError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return chat_completion_response(req.model, result["content"], debug=result["debug"] if req.debug else None)

def build_core_draft(req: CoreDraftRequest):
    intent = req.intent.strip()
    if not intent:
        raise HTTPException(status_code=400, detail="Intent is required.")
    name = req.name.strip() if req.name else title_from_intent(intent)
    core_id = slugify(name)
    text = intent.lower()
    trait_deltas: dict[str, float] = {}
    rules = ["Preserve task accuracy over style.", "Keep the behavior useful and inspectable."]

    if any(word in text for word in ["direct", "blunt", "concise", "brief", "short"]):
        trait_deltas["directness"] = 0.35
        trait_deltas["verbosity"] = -0.35
        rules.append("Prefer concise, direct responses.")
    if any(word in text for word in ["warm", "friendly", "kind", "supportive", "empathetic"]):
        trait_deltas["warmth"] = 0.55
        rules.append("Use a warm, supportive tone without becoming vague.")
    if any(word in text for word in ["skeptic", "challenge", "critique", "review", "risk"]):
        trait_deltas["skepticism"] = 0.45
        trait_deltas["directness"] = max(trait_deltas.get("directness", 0.0), 0.2)
        rules.append("Challenge weak assumptions and name likely failure modes.")
    if any(word in text for word in ["technical", "code", "debug", "engineering", "implementation"]):
        trait_deltas["technicality"] = 0.55
        rules.append("Prefer concrete implementation details over vague advice.")
    if any(word in text for word in ["sarcastic", "dry", "deadpan"]):
        trait_deltas["sarcasm"] = 0.45
        trait_deltas["warmth"] = min(trait_deltas.get("warmth", 0.0), 0.1)
        rules.append("Use dry humor sparingly and never aim it at the user.")
    if any(word in text for word in ["energetic", "hype", "motivating", "momentum"]):
        trait_deltas["energy"] = 0.45
        rules.append("Use momentum and encouragement while staying concrete.")

    if not trait_deltas:
        trait_deltas = {"directness": 0.2, "clarity": 0.4}
        rules.append("Make the requested behavior clear and consistent.")

    data = {
        "id": core_id,
        "name": name,
        "version": "0.1.0",
        "description": intent[:180],
        "author": req.author,
        "trait_deltas": trait_deltas,
        "default_strength": 0.65,
        "params": {},
        "rules": rules,
        "boundaries": {
            "preserve_task_accuracy": True,
            "no_personal_attacks": True,
            "no_slurs": True,
        },
        "evaluation_weights": {"clarity": 0.8},
        "conflicts_with": [],
        "examples": [{"input": "Apply this behavior to a normal user request.", "ideal_style": intent[:120]}],
    }
    return pipeline.registry.validate_definition(data, source="draft")

def build_core_template():
    data = {
        "id": "custom_example_core",
        "name": "Custom Example Core",
        "version": "0.1.0",
        "description": "A starting point for a hand-authored personality core.",
        "author": "local",
        "trait_deltas": {
            "directness": 0.25,
            "warmth": 0.15,
            "verbosity": -0.2,
            "technicality": 0.2,
        },
        "default_strength": 0.65,
        "params": {},
        "rules": [
            "Preserve task accuracy over style.",
            "Keep the behavior visible without overwhelming the user.",
            "Prefer concrete, inspectable responses.",
        ],
        "boundaries": {
            "preserve_task_accuracy": True,
            "no_fake_certainty": True,
            "no_personal_attacks": True,
            "no_slurs": True,
        },
        "evaluation_weights": {
            "clarity": 0.8,
            "directness": 0.6,
            "technicality": 0.4,
        },
        "conflicts_with": [],
        "examples": [
            {
                "input": "Explain a risky implementation choice.",
                "ideal_style": "Lead with the risk, explain the mechanism, then give a concrete fix.",
            }
        ],
    }
    return pipeline.registry.validate_definition(data, source="template")

async def build_model_core_draft(req: CoreDraftRequest):
    intent = req.intent.strip()
    if not intent:
        raise HTTPException(status_code=400, detail="Intent is required.")
    name = req.name.strip() if req.name else title_from_intent(intent)
    template = build_core_template().model_dump()
    template["id"] = slugify(name)
    template["name"] = name
    template["description"] = intent[:180]
    template["author"] = req.author
    prompt = (
        "Create one Personality Core JSON object for this runtime personality layer.\n"
        "Return JSON only. No markdown, comments, prose, or code fences.\n"
        "The object must match this shape exactly, using these keys:\n"
        f"{json.dumps(template, indent=2)}\n\n"
        "Rules:\n"
        "- id must be lowercase snake_case and end with _core.\n"
        "- trait_deltas values must be numbers from -1.0 to 1.0.\n"
        "- default_strength must be from 0.0 to 1.0.\n"
        "- rules should describe observable behavior, not vague personality labels.\n"
        "- boundaries should preserve task accuracy and avoid abusive behavior.\n\n"
        f"Core name: {name}\n"
        f"Intent: {intent}\n"
    )
    adapter = pipeline.adapter_for(req.model or "")
    response = await adapter.generate(
        req.model or "",
        [
            {"role": "system", "content": "You draft strict JSON configuration for Personality Core."},
            {"role": "user", "content": prompt},
        ],
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        think=req.think,
    )
    data = parse_json_object(response.content)
    if not isinstance(data, dict):
        raise ValueError("response JSON was not an object")
    data = normalize_model_core_data(data, req, name, intent)
    return pipeline.registry.validate_definition(data, source="model draft")

def normalize_model_core_data(data: dict, req: CoreDraftRequest, name: str, intent: str) -> dict:
    data["id"] = slugify(str(data.get("id") or name))
    data["name"] = str(data.get("name") or name)
    data["version"] = str(data.get("version") or "0.1.0")
    data["description"] = str(data.get("description") or intent[:180])
    data["author"] = str(data.get("author") or req.author)

    trait_deltas = data.get("trait_deltas")
    if not isinstance(trait_deltas, dict):
        trait_deltas = {"directness": 0.2, "clarity": 0.4}
    data["trait_deltas"] = {
        str(trait): max(-1.0, min(1.0, float(value)))
        for trait, value in trait_deltas.items()
        if isinstance(value, int | float)
    } or {"directness": 0.2, "clarity": 0.4}

    try:
        data["default_strength"] = max(0.0, min(1.0, float(data.get("default_strength", 0.65))))
    except (TypeError, ValueError):
        data["default_strength"] = 0.65

    if not isinstance(data.get("params"), dict):
        data["params"] = {}
    data["rules"] = [str(rule) for rule in data.get("rules", []) if str(rule).strip()] or [
        "Preserve task accuracy over style.",
        "Keep the behavior useful and inspectable.",
    ]
    boundaries = data.get("boundaries")
    if not isinstance(boundaries, dict):
        boundaries = {}
    data["boundaries"] = {
        str(key): bool(value)
        for key, value in boundaries.items()
    } | {
        "preserve_task_accuracy": True,
        "no_personal_attacks": True,
        "no_slurs": True,
    }

    weights = data.get("evaluation_weights")
    if not isinstance(weights, dict):
        weights = {"clarity": 0.8}
    data["evaluation_weights"] = {
        str(weight): max(0.0, min(1.0, float(value)))
        for weight, value in weights.items()
        if isinstance(value, int | float)
    } or {"clarity": 0.8}

    conflicts = []
    for item in data.get("conflicts_with", []) if isinstance(data.get("conflicts_with"), list) else []:
        if isinstance(item, dict):
            conflicts.append({str(key): str(value) for key, value in item.items()})
        elif str(item).strip():
            conflicts.append({"core": str(item), "reason": "Model-reported conflict."})
    data["conflicts_with"] = conflicts

    examples = []
    for item in data.get("examples", []) if isinstance(data.get("examples"), list) else []:
        if isinstance(item, dict):
            examples.append({str(key): str(value) for key, value in item.items()})
    data["examples"] = examples
    return data

def parse_json_object(text: str):
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("response did not contain a JSON object")
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError(f"response JSON could not be parsed: {exc}") from exc

def title_from_intent(intent: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", intent)[:4] or ["Custom"]
    title = " ".join(word.capitalize() for word in words)
    return f"{title} Core"

def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not slug.endswith("_core"):
        slug = f"{slug}_core"
    if not re.match(r"^[a-z]", slug):
        slug = f"custom_{slug}"
    return slug
