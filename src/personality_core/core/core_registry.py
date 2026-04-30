from __future__ import annotations
from pathlib import Path
import json
import re
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
        return self.validate_definition(data, source=str(path))

    def validate_definition(self, data: dict, source: str = "core") -> CoreDefinition:
        try:
            core = CoreDefinition.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid core {source}: {exc}") from exc
        if not re.fullmatch(r"[a-z][a-z0-9_]*", core.id):
            raise ValueError(f"Core {core.id} id must use lowercase letters, numbers, and underscores.")
        for k, v in core.trait_deltas.items():
            if not -1.0 <= v <= 1.0:
                raise ValueError(f"Core {core.id} trait delta {k} out of range: {v}")
        if not 0.0 <= core.default_strength <= 1.0:
            raise ValueError(f"Core {core.id} default_strength must be 0..1")
        return core

    def install(self, data: dict, overwrite: bool = False) -> CoreDefinition:
        core = self.validate_definition(data, source="install")
        self.cores_dir.mkdir(parents=True, exist_ok=True)
        path = self.cores_dir / f"{core.id}.json"
        if path.exists() and not overwrite:
            raise ValueError(f"Core already exists: {core.id}")
        path.write_text(json.dumps(core.model_dump(), indent=2), encoding="utf-8")
        self.load()
        return core

    def list(self) -> list[CoreDefinition]:
        return list(self._cores.values())

    def get(self, core_id: str) -> CoreDefinition:
        if core_id not in self._cores:
            raise KeyError(f"Unknown core: {core_id}")
        return self._cores[core_id]

    def has(self, core_id: str) -> bool:
        return core_id in self._cores
