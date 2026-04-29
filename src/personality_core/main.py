from __future__ import annotations
from pathlib import Path
import json
import typer
import uvicorn
from rich import print
from personality_core.config import DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR
from personality_core.core.core_registry import CoreRegistry
from personality_core.core.core_stack import CoreStackResolver
from personality_core.schemas import CoreRef
from personality_core.core.compiler import CoreCompiler

app = typer.Typer(help="Personality Core CLI")

@app.command()
def serve(host: str = "127.0.0.1", port: int = 8787):
    """Run the OpenAI-compatible proxy server."""
    uvicorn.run("personality_core.app:api", host=host, port=port, reload=False)

@app.command("list-cores")
def list_cores():
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    for core in reg.list():
        print(f"[bold]{core.id}[/bold] - {core.description}")

@app.command()
def inspect(core_id: str):
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    print_json(reg.get(core_id).model_dump())

@app.command()
def validate(path: Path):
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    core = reg.validate_file(path)
    print(f"[green]Valid core:[/green] {core.id}")

@app.command()
def stack(cores: str):
    refs = parse_core_refs(cores)
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    resolved = CoreStackResolver(reg).resolve(refs)
    print_json(resolved.model_dump())

@app.command()
def prompt(cores: str, model: str = "ollama/gemma4:e4b"):
    refs = parse_core_refs(cores)
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    resolved = CoreStackResolver(reg).resolve(refs)
    compiled = CoreCompiler(DEFAULT_MODEL_PROFILES_DIR).compile(resolved, mode="debugging", model=model)
    print(compiled)

@app.command()
def test(model: str = "ollama/gemma4:e4b", cores: str = "technical_core:0.9,sarcasm_core:0.7", turns: int = 3):
    """Print a suggested manual drift test prompt sequence."""
    print("Run the server, then send repeated requests with this core stack:")
    print(parse_core_refs(cores))
    for i in range(turns):
        print(f"Turn {i+1}: Explain one more reason retry loops with shared mutable state are dangerous.")

def parse_core_refs(spec: str) -> list[CoreRef]:
    refs = []
    for part in [p.strip() for p in spec.split(",") if p.strip()]:
        if ":" in part:
            cid, strength = part.split(":", 1)
            refs.append(CoreRef(id=cid, strength=float(strength)))
        else:
            refs.append(CoreRef(id=part))
    return refs

def print_json(data):
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    app()
