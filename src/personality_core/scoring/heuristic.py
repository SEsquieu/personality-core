from __future__ import annotations
import re
from personality_core.schemas import ResolvedStack

PROFANITY = {"damn", "hell", "shit", "fuck", "fucking", "bullshit"}
SARCASTIC_MARKERS = ["sure", "obviously", "because apparently", "congratulations", "shocking", "what could possibly"]

def score_text(text: str, resolved: ResolvedStack) -> dict:
    lower = text.lower()
    words = re.findall(r"\w+", lower)
    word_count = max(len(words), 1)
    profanity_count = sum(1 for w in words if w in PROFANITY)
    sarcasm_hits = sum(1 for s in SARCASTIC_MARKERS if s in lower)
    avg_sentence_words = word_count / max(len(re.split(r"[.!?]+", text)), 1)
    scores = {
        "profanity": min(1.0, profanity_count / 3),
        "sarcasm": min(1.0, sarcasm_hits / 2),
        "verbosity": min(1.0, word_count / 260),
        "directness": 0.75 if word_count < 180 else 0.45,
        "technicality": 0.8 if any(t in lower for t in ["state", "config", "api", "function", "loop", "error", "runtime", "deploy", "code"]) else 0.45,
        "clarity": 0.8 if avg_sentence_words < 28 else 0.55,
        "non_abusive": 1.0,
    }
    target = resolved.resolved_traits
    diffs = []
    for key in ["profanity", "sarcasm", "verbosity", "directness", "technicality"]:
        if key in target and key in scores:
            diffs.append(abs(target[key] - scores[key]))
    core_match = max(0.0, 1.0 - (sum(diffs) / max(len(diffs), 1)))
    issues = []
    if target.get("sarcasm", 0) > 0.45 and scores["sarcasm"] < 0.2:
        issues.append("Sarcasm Core target appears under-expressed.")
    if target.get("profanity", 0) > 0.25 and scores["profanity"] < 0.1:
        issues.append("Profanity Core target appears under-expressed.")
    if target.get("verbosity", 0.5) < 0.35 and scores["verbosity"] > 0.55:
        issues.append("Low Verbosity Core target appears under-expressed.")
    return {"core_match": round(core_match, 3), "repair_needed": core_match < 0.78, "scores": scores, "issues": issues}
