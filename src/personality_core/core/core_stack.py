from __future__ import annotations
from typing import Any
from personality_core.schemas import CoreRef, ResolvedStack
from personality_core.core.core_registry import CoreRegistry

DEFAULT_BASE_TRAITS = {
    "directness": 0.5,
    "warmth": 0.5,
    "sarcasm": 0.0,
    "chaos": 0.0,
    "verbosity": 0.5,
    "skepticism": 0.3,
    "profanity": 0.0,
    "technicality": 0.5,
    "professionalism": 0.5,
    "energy": 0.4,
    "consistency": 0.5,
}

class CoreStackResolver:
    def __init__(self, registry: CoreRegistry):
        self.registry = registry

    def resolve(self, core_refs: list[CoreRef], base_traits: dict[str, float] | None = None) -> ResolvedStack:
        base = {**DEFAULT_BASE_TRAITS, **(base_traits or {})}
        resolved = dict(base)
        boundaries: dict[str, bool] = {}
        rules: list[str] = []
        contracts: list[dict[str, Any]] = []
        active: list[dict[str, Any]] = []
        core_trace: list[dict[str, Any]] = []
        conflicts: list[dict[str, Any]] = []
        installed_ids = [c.id for c in core_refs]

        for ref in core_refs:
            core = self.registry.get(ref.id)
            strength = core.default_strength if ref.strength is None else max(0.0, min(1.0, ref.strength))
            merged_params = {**core.params, **(ref.params or {})}
            trait_effects: dict[str, float] = {}
            for trait, delta in core.trait_deltas.items():
                effect = delta * strength
                trait_effects[trait] = round(effect, 3)
                resolved[trait] = resolved.get(trait, 0.5) + effect
            for key, value in core.boundaries.items():
                boundaries[key] = bool(boundaries.get(key, False) or value)
            rules.extend(core.rules)
            for contract in core.contracts:
                contracts.append({**contract, "core_id": core.id, "core_name": core.name, "strength": strength})
            for conflict in core.conflicts_with:
                other = conflict.get("core_id")
                if other in installed_ids:
                    conflicts.append({"cores": [core.id, other], "severity": "medium", "reason": conflict.get("reason", "Potential tone conflict."), "resolution": "allow_with_constraints"})
            active.append({"id": core.id, "name": core.name, "kind": core.kind, "strength": strength, "params": merged_params})
            core_trace.append({"id": core.id, "name": core.name, "strength": strength, "trait_effects": trait_effects})

        for trait, val in list(resolved.items()):
            resolved[trait] = max(0.0, min(1.0, val))
        return ResolvedStack(base_traits=base, resolved_traits=resolved, boundaries=boundaries, rules=rules, contracts=contracts, active_cores=active, core_trace=core_trace, conflicts=conflicts)
