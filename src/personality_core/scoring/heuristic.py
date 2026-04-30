from __future__ import annotations
import re
from personality_core.schemas import ResolvedStack

PROFANITY = {"damn", "hell", "shit", "fuck", "fucking", "bullshit"}
SARCASTIC_MARKERS = ["sure", "obviously", "because apparently", "congratulations", "shocking", "what could possibly"]
CORE_TRAIT_KEYS = {
    "technical_core": ["technicality", "directness"],
    "sarcasm_core": ["sarcasm", "clarity", "non_abusive"],
    "profanity_core": ["profanity", "clarity", "non_abusive"],
    "low_verbosity_core": ["verbosity", "directness", "clarity"],
    "warmth_core": ["warmth", "clarity", "non_abusive"],
    "professional_support_core": ["professionalism", "clarity", "non_abusive"],
    "chaos_core": ["chaos", "technicality", "clarity"],
    "skepticism_core": ["skepticism", "technicality", "clarity"],
    "hype_core": ["energy", "clarity"],
    "stability_core": ["consistency", "clarity", "non_abusive"],
}

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
        "warmth": 0.7 if any(t in lower for t in ["help", "understand", "step", "clear", "let's"]) else 0.45,
        "professionalism": 0.75 if any(t in lower for t in ["please", "support", "customer", "issue", "resolve"]) else 0.5,
        "chaos": 0.65 if any(t in lower for t in ["wild", "mess", "chaos", "absurd", "weird"]) else 0.15,
        "skepticism": 0.75 if any(t in lower for t in ["assumption", "risk", "failure", "unless", "but"]) else 0.35,
        "energy": 0.7 if any(t in lower for t in ["great", "move", "ship", "momentum", "now"]) else 0.35,
        "consistency": 0.7 if word_count < 220 else 0.5,
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
    core_scores = score_cores(scores, resolved)
    return {"core_match": round(core_match, 3), "repair_needed": core_match < 0.78, "scores": scores, "core_scores": core_scores, "issues": issues}

def score_cores(scores: dict[str, float], resolved: ResolvedStack) -> dict[str, float]:
    target = resolved.resolved_traits
    results: dict[str, float] = {}
    for core in resolved.active_cores:
        core_id = core["id"]
        keys = CORE_TRAIT_KEYS.get(core_id)
        if not keys:
            keys = [k for k in target if k in scores]
        diffs = [abs(target[k] - scores[k]) for k in keys if k in target and k in scores]
        if diffs:
            results[core_id] = round(max(0.0, 1.0 - (sum(diffs) / len(diffs))), 3)
    return results
