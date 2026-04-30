from __future__ import annotations
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

@router.post("/v1/cores/draft")
def draft_core(req: CoreDraftRequest):
    return {"core": build_core_draft(req).model_dump()}

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
