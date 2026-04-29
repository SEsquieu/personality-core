from __future__ import annotations
import time, uuid

def chat_completion_response(model: str, content: str, debug: dict | None = None) -> dict:
    message = {"role": "assistant", "content": content}
    if debug is not None:
        message["core_debug"] = debug
    return {
        "id": f"chatcmpl-pcore-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
