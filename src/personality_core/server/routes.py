from __future__ import annotations
from pathlib import Path
from fastapi import APIRouter, HTTPException
from personality_core.schemas import ChatCompletionRequest
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

@router.post("/v1/chat/completions")
async def chat(req: ChatCompletionRequest):
    if req.stream:
        raise HTTPException(status_code=400, detail="Streaming is not implemented in this MVP.")
    try:
        result = await pipeline.run(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return chat_completion_response(req.model, result["content"], debug=result["debug"] if req.debug else None)
