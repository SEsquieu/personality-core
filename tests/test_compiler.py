from pathlib import Path
from personality_core.core.core_registry import CoreRegistry
from personality_core.core.core_stack import CoreStackResolver
from personality_core.core.compiler import CoreCompiler
from personality_core.schemas import CoreRef

def test_compiler_mentions_core():
    reg = CoreRegistry(Path("cores"))
    resolved = CoreStackResolver(reg).resolve([CoreRef(id="sarcasm_core", strength=0.8)])
    prompt = CoreCompiler(Path("model_profiles")).compile(resolved, "debugging", "ollama/gemma4:e4b")
    assert "Sarcasm Core" in prompt
