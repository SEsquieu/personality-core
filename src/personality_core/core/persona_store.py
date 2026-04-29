from __future__ import annotations
from pathlib import Path
import json
from personality_core.schemas import CoreRef

class PersonaStore:
    def __init__(self, personalities_dir: Path):
        self.personalities_dir = Path(personalities_dir)

    def load(self, persona_id: str | None) -> tuple[dict[str, float], list[CoreRef], dict]:
        if not persona_id:
            return {}, [], {}
        path = self.personalities_dir / f"{persona_id}.json"
        if not path.exists():
            raise KeyError(f"Unknown personality preset: {persona_id}")
        data = json.loads(path.read_text(encoding="utf-8"))
        base_traits = data.get("base_traits", {})
        cores = [CoreRef.model_validate(c) for c in data.get("cores", [])]
        return base_traits, cores, data
