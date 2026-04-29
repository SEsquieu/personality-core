from __future__ import annotations

KEYWORDS = {
    "debugging": ["bug", "error", "failed", "traceback", "stack", "retry", "config", "code"],
    "teaching": ["explain", "teach", "learn", "walk me through"],
    "writing": ["rewrite", "draft", "post", "email", "copy"],
    "planning": ["plan", "roadmap", "strategy", "scope"],
}

def detect_mode(messages: list[dict]) -> str:
    text = " ".join(str(m.get("content", "")) for m in messages[-4:]).lower()
    for mode, words in KEYWORDS.items():
        if any(w in text for w in words):
            return mode
    return "casual_chat"
