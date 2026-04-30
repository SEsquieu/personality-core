from __future__ import annotations
from dataclasses import dataclass, field
import re
from typing import Any
from personality_core.schemas import ResolvedStack


@dataclass
class MutationReport:
    applied: list[dict[str, Any]] = field(default_factory=list)

    @property
    def changed(self) -> bool:
        return any(item.get("count", 0) > 0 for item in self.applied)


def apply_mutations(text: str, resolved: ResolvedStack) -> tuple[str, dict[str, Any]]:
    current = text
    report = MutationReport()
    for mutation in resolved.mutations:
        if mutation.get("type") == "replace_terms":
            current, item = apply_replace_terms(current, mutation)
            report.applied.append(item)
    return current, {"changed": report.changed, "applied": report.applied}


def apply_replace_terms(text: str, mutation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    terms = mutation.get("terms", {})
    if not isinstance(terms, dict) or not terms:
        return text, mutation_report(mutation, 0)
    effective_rate = mutation_rate(mutation)
    if effective_rate <= 0:
        return text, mutation_report(mutation, 0)
    whole_words = bool(mutation.get("whole_words", True))
    preserve_case = bool(mutation.get("preserve_case", True))
    count = 0
    current = text
    for source, target in terms.items():
        source_text = str(source)
        target_text = str(target)
        pattern = re.escape(source_text)
        if whole_words:
            pattern = rf"\b{pattern}\b"
        occurrence = 0

        def replace(match: re.Match[str]) -> str:
            nonlocal occurrence, count
            occurrence += 1
            if not should_apply_occurrence(occurrence, effective_rate):
                return match.group(0)
            count += 1
            return match_case(match.group(0), target_text) if preserve_case else target_text

        current = re.sub(pattern, replace, current, flags=re.IGNORECASE)
    return current, mutation_report(mutation, count)


def mutation_rate(mutation: dict[str, Any]) -> float:
    try:
        rate = float(mutation.get("rate", 1.0))
    except (TypeError, ValueError):
        rate = 1.0
    try:
        strength = float(mutation.get("strength", 1.0))
    except (TypeError, ValueError):
        strength = 1.0
    return max(0.0, min(1.0, rate * strength))


def should_apply_occurrence(occurrence: int, rate: float) -> bool:
    if rate >= 1:
        return True
    if rate <= 0:
        return False
    interval = max(1, round(1 / rate))
    return occurrence % interval == 0


def match_case(source: str, target: str) -> str:
    if source.isupper():
        return target.upper()
    if source[:1].isupper():
        return target[:1].upper() + target[1:]
    return target


def mutation_report(mutation: dict[str, Any], count: int) -> dict[str, Any]:
    return {
        "type": mutation.get("type"),
        "core_id": mutation.get("core_id"),
        "core_name": mutation.get("core_name"),
        "count": count,
        "rate": mutation.get("rate", 1.0),
        "strength": mutation.get("strength", 1.0),
    }
