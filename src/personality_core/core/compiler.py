from __future__ import annotations
from pathlib import Path
import json
from personality_core.schemas import ResolvedStack

TRAIT_LINES = {
    "directness": (0.7, "Be direct. Avoid evasive filler."),
    "warmth": (0.7, "Use a warm, supportive tone without becoming vague."),
    "sarcasm": (0.45, "Use dry, occasional sarcasm when reacting to flawed decisions. Do not aim sarcasm at the user personally."),
    "chaos": (0.45, "Allow playful, strange metaphors, but preserve usefulness."),
    "verbosity": (0.7, "Provide enough detail when needed."),
    "skepticism": (0.6, "Challenge weak assumptions and point out likely failure modes."),
    "profanity": (0.25, "Mild profanity is allowed only as non-targeted emphasis. No slurs, threats, or personal attacks."),
    "technicality": (0.7, "Prefer technically precise, implementation-aware answers."),
    "professionalism": (0.75, "Use polished, professional language."),
    "energy": (0.7, "Use high-energy phrasing, but pair momentum with concrete substance."),
    "consistency": (0.7, "Maintain this voice consistently across turns."),
}

class CoreCompiler:
    def __init__(self, model_profiles_dir: Path):
        self.model_profiles_dir = Path(model_profiles_dir)

    def load_model_profile(self, model: str) -> dict:
        safe = model.replace("/", "_").replace(":", "_")
        path = self.model_profiles_dir / f"{safe}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if model.startswith("ollama/"):
            path = self.model_profiles_dir / "ollama_default.json"
        else:
            path = self.model_profiles_dir / "openai_default.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def compile(self, resolved: ResolvedStack, mode: str, model: str, drift_note: str | None = None) -> str:
        profile = self.load_model_profile(model)
        hints = profile.get("compiler_hints", {})
        strength = float(hints.get("style_instruction_strength", 1.0))
        traits = resolved.resolved_traits
        lines: list[str] = []
        lines.append("You are operating through Personality Core, a runtime personality control layer.")
        lines.append("Follow the active core stack as behavioral policy. Preserve the user's task and factual accuracy above style.")
        lines.append(f"Current mode: {mode}.")
        lines.append("Active cores: " + ", ".join(f"{c['name']}@{c['strength']:.2f}" for c in resolved.active_cores) + ".")
        lines.append("Resolved trait targets:")
        for k in sorted(traits):
            lines.append(f"- {k}: {traits[k]:.2f}")
        lines.append("Behavioral instructions:")
        for trait, (threshold, instruction) in TRAIT_LINES.items():
            val = traits.get(trait, 0.0)
            if val * strength >= threshold:
                lines.append(f"- {instruction}")
        if traits.get("verbosity", 0.5) < 0.35:
            lines.append("- Keep the answer concise. No bloated preamble.")
        if traits.get("formality", 0.5) < 0.35:
            lines.append("- Use casual language where appropriate.")
        if resolved.rules:
            lines.append("Core rules:")
            for r in resolved.rules[:16]:
                lines.append(f"- {r}")
        if resolved.contracts:
            lines.append("Output contracts:")
            for contract in resolved.contracts[:8]:
                contract_type = contract.get("type", "behavior")
                lines.append(f"- {contract.get('core_name', contract.get('core_id', 'core'))}: {contract_type}")
                if contract_type == "json_object":
                    lines.append("  Return exactly one valid JSON object. Do not wrap it in markdown or prose.")
                    required = contract.get("required_fields", [])
                    if required:
                        lines.append("  Required fields: " + ", ".join(str(field) for field in required) + ".")
                    schema = contract.get("schema")
                    if schema:
                        lines.append("  JSON schema: " + json.dumps(schema, separators=(",", ":")))
                for instruction in contract.get("instructions", [])[:4]:
                    lines.append(f"  {instruction}")
        if resolved.boundaries:
            lines.append("Hard boundaries:")
            for k, v in resolved.boundaries.items():
                if v:
                    lines.append(f"- Enforce: {k}")
        if resolved.conflicts:
            lines.append("Core conflicts detected. Resolve them conservatively:")
            for c in resolved.conflicts[:4]:
                lines.append(f"- {', '.join(c['cores'])}: {c['reason']} Resolution: {c['resolution']}.")
        if drift_note:
            lines.append(f"Drift correction: {drift_note}")
        if hints.get("repeat_style_constraints"):
            lines.append("Reminder: style is allowed, but usefulness and safety are mandatory. Do not become generic unless the user asks for it.")
        return "\n".join(lines)
