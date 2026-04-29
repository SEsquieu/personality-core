from __future__ import annotations
from pathlib import Path
import json
from pydantic import ValidationError
from personality_core.schemas import CoreDefinition

class CoreRegistry:
    def __init__(self, cores_dir: Path):
        self.cores_dir = Path(cores_dir)
        self._cores: dict[str, CoreDefinition] = {}
        self.load()

    def load(self) -> None:
        self._cores.clear()
        if not self.cores_dir.exists():
            return
        for path in sorted(self.cores_dir.glob("*.json")):
            core = self.validate_file(path)
            self._cores[core.id] = core

    def validate_file(self, path: Path) -> CoreDefinition:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        try:
            core = CoreDefinition.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid core {path}: {exc}") from exc
        for k, v in core.trait_deltas.items():
            if not -1.0 <= v <= 1.0:
                raise ValueError(f"Core {core.id} trait delta {k} out of range: {v}")
        if not 0.0 <= core.default_strength <= 1.0:
            raise ValueError(f"Core {core.id} default_strength must be 0..1")
        return core

    def list(self) -> list[CoreDefinition]:
        return list(self._cores.values())

    def get(self, core_id: str) -> CoreDefinition:
        if core_id not in self._cores:
            raise KeyError(f"Unknown core: {core_id}")
        return self._cores[core_id]

    def has(self, core_id: str) -> bool:
        return core_id in self._cores
