from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, HTTPException
from personality_core.adapters.base import ModelAdapterError
from personality_core.schemas import ChatCompletionRequest, ChatMessage, CompareRequest
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
