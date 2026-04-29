from pathlib import Path
from personality_core.core.core_registry import CoreRegistry
from personality_core.core.core_stack import CoreStackResolver
from personality_core.schemas import CoreRef

def test_resolve_stack():
    reg = CoreRegistry(Path("cores"))
    resolved = CoreStackResolver(reg).resolve([CoreRef(id="technical_core", strength=1.0)])
    assert resolved.resolved_traits["technicality"] >= 0.9
