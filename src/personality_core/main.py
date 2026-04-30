from __future__ import annotations
from pathlib import Path
import asyncio
import json
import typer
import uvicorn
from rich import print
from rich.panel import Panel
from personality_core.adapters.base import ModelAdapterError
from personality_core.config import DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR, DEFAULT_MODEL
from personality_core.core.core_registry import CoreRegistry
from personality_core.core.core_stack import CoreStackResolver
from personality_core.core.pipeline import PersonalityPipeline
from personality_core.schemas import ChatCompletionRequest, ChatMessage, CoreRef
from personality_core.core.compiler import CoreCompiler

app = typer.Typer(help="Personality Core CLI")

DEMO_PROMPTS = {
    "retry_loop": "Explain why retries hide real errors.",
    "angry_customer": "A customer is angry because their export failed twice. Draft the response.",
    "code_review": "Review this pattern: a retry loop mutates shared state and swallows the original exception.",
    "startup_pitch": "Pressure-test my idea for an AI-powered meeting notes app.",
    "debugging": "Explain why mutating shared state inside a retry loop is dangerous.",
}

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
def stack(cores: str = typer.Option(..., "--cores", "-c", help="Comma-separated core_id[:strength] entries.")):
    refs = parse_core_refs(cores)
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    resolved = CoreStackResolver(reg).resolve(refs)
    print_json(resolved.model_dump())

@app.command()
def prompt(
    cores: str = typer.Option(..., "--cores", "-c", help="Comma-separated core_id[:strength] entries."),
    model: str = DEFAULT_MODEL,
):
    refs = parse_core_refs(cores)
    reg = CoreRegistry(DEFAULT_CORES_DIR)
    resolved = CoreStackResolver(reg).resolve(refs)
    compiled = CoreCompiler(DEFAULT_MODEL_PROFILES_DIR).compile(resolved, mode="debugging", model=model)
    print(compiled)

@app.command()
def test(model: str = DEFAULT_MODEL, cores: str = "technical_core:0.9,sarcasm_core:0.7", turns: int = 3):
    """Print a suggested manual drift test prompt sequence."""
    print("Run the server, then send repeated requests with this core stack:")
    print(parse_core_refs(cores))
    for i in range(turns):
        print(f"Turn {i+1}: Explain one more reason retry loops with shared mutable state are dangerous.")

@app.command()
def chat(
    prompt: str,
    model: str = DEFAULT_MODEL,
    cores: str = "technical_core:0.95,sarcasm_core:0.7,low_verbosity_core:0.75",
    personality: str | None = None,
    stabilizer: bool = False,
    debug: bool = False,
    max_tokens: int = 300,
    temperature: float | None = None,
    think: bool = False,
):
    """Run one prompt through a core stack without starting the HTTP server."""
    req = ChatCompletionRequest(
        model=model,
        messages=[ChatMessage(role="user", content=prompt)],
        personality=personality,
        cores=parse_core_refs(cores) if cores else [],
        stabilizer=stabilizer,
        debug=debug,
        max_tokens=max_tokens,
        temperature=temperature,
        think=think,
    )
    try:
        result = asyncio.run(run_request(req))
    except ModelAdapterError as exc:
        print(f"[red]Model backend error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    print(result["content"])
    for warning in result.get("warnings", []):
        print(f"\n[yellow]Warning:[/yellow] {warning}")
    if debug:
        print("\n[bold]Core debug[/bold]")
        print_json(result["debug"])

@app.command()
def compare(
    prompt: str = typer.Argument("Explain why retries hide real errors."),
    model: str = DEFAULT_MODEL,
    personalities: str = "professional_support,deadpan_debugger,patient_tutor,startup_cofounder,chaos_goblin",
    max_tokens: int = 260,
    temperature: float | None = None,
    think: bool = False,
    show_prompt: bool = False,
    demo: str | None = None,
    summary_only: bool = typer.Option(False, "--summary", help="Show diagnostics only, without full model responses."),
    json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON instead of Rich panels."),
    save: Path | None = None,
):
    """Run one prompt through several personality presets."""
    if demo:
        try:
            prompt = DEMO_PROMPTS[demo]
        except KeyError as exc:
            print(f"[red]Unknown demo prompt:[/red] {demo}")
            print("Available demos: " + ", ".join(sorted(DEMO_PROMPTS)))
            raise typer.Exit(code=1) from exc
    selected = [p.strip() for p in personalities.split(",") if p.strip()]
    if not selected:
        print("[red]No personalities selected.[/red]")
        raise typer.Exit(code=1)

    if not json_output:
        print("[bold]Personality Core comparison[/bold]")
        print(f"Model: [bold]{model}[/bold]")
        if demo:
            print(f"Demo: [bold]{demo}[/bold]")
        if show_prompt:
            print(f"Prompt: {prompt}")
        print()

    pipeline = PersonalityPipeline(DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR)
    records = []
    for persona_id in selected:
        req = ChatCompletionRequest(
            model=model,
            messages=[ChatMessage(role="user", content=prompt)],
            personality=persona_id,
            max_tokens=max_tokens,
            temperature=temperature,
            think=think,
            debug=True,
        )
        try:
            result = asyncio.run(pipeline.run(req))
        except KeyError as exc:
            record = {"personality": persona_id, "error": str(exc)}
            records.append(record)
            if not json_output:
                print(Panel(str(exc), title=f"{persona_id}", border_style="red"))
            continue
        except ModelAdapterError as exc:
            if json_output:
                print_json({"error": str(exc), "model": model, "prompt": prompt, "results": records})
            else:
                print(Panel(str(exc), title="Model backend error", border_style="red"))
            raise typer.Exit(code=1) from exc

        debug = result["debug"]
        evaluation = debug["evaluation"]
        resolved = debug["resolved"]
        record = {
            "personality": persona_id,
            "model": model,
            "prompt": prompt,
            "content": result["content"],
            "warnings": result.get("warnings", []),
            "mode": debug["mode"],
            "done_reason": debug.get("model_response", {}).get("done_reason"),
            "active_cores": [c["id"] for c in resolved["active_cores"]],
            "core_match": evaluation["core_match"],
            "core_scores": evaluation.get("core_scores", {}),
            "issues": evaluation.get("issues", []),
        }
        records.append(record)
        if json_output:
            continue

        active = ", ".join(c["id"] for c in resolved["active_cores"])
        core_scores = ", ".join(f"{k}={v}" for k, v in evaluation.get("core_scores", {}).items()) or "none"
        issues = "; ".join(evaluation.get("issues", [])) or "none"
        warnings = "; ".join(result.get("warnings", [])) or "none"
        panel_body = (
            f"[dim]cores:[/dim] {active}\n"
            f"[dim]core_match:[/dim] {evaluation['core_match']}  "
            f"[dim]mode:[/dim] {debug['mode']}  "
            f"[dim]done:[/dim] {debug.get('model_response', {}).get('done_reason')}\n"
            f"[dim]core_scores:[/dim] {core_scores}\n"
            f"[dim]issues:[/dim] {issues}\n"
            f"[dim]warnings:[/dim] {warnings}"
        )
        if not summary_only:
            panel_body += f"\n\n{result['content']}"
        print(Panel(panel_body, title=persona_id, border_style="cyan"))
        print()

    output = {"model": model, "prompt": prompt, "demo": demo, "results": records}
    if save:
        save.parent.mkdir(parents=True, exist_ok=True)
        save.write_text(json.dumps(output, indent=2), encoding="utf-8")
        if not json_output:
            print(f"[green]Saved comparison:[/green] {save}")
    if json_output:
        print_json(output)

@app.command()
def demo(model: str = DEFAULT_MODEL):
    """Show fun starter stacks for the first five minutes after clone."""
    examples = [
        (
            "Deadpan Debugger",
            "technical_core:0.95,sarcasm_core:0.65,skepticism_core:0.75,low_verbosity_core:0.7,stability_core:0.85",
            "Explain why mutating shared state inside a retry loop is dangerous.",
        ),
        (
            "Professional Support",
            "professional_support_core:1.0,warmth_core:0.5,low_verbosity_core:0.55,stability_core:0.9",
            "A customer is angry because their export failed twice. Draft the response.",
        ),
        (
            "Startup Cofounder",
            "technical_core:0.7,skepticism_core:0.85,hype_core:0.65,low_verbosity_core:0.45",
            "Pressure-test my idea for an AI-powered meeting notes app.",
        ),
        (
            "Chaos Stack",
            "chaos_core:0.8,technical_core:0.65,profanity_core:0.35,stability_core:0.5",
            "Explain why hiding errors behind retries makes debugging miserable.",
        ),
    ]
    print("[bold]Personality Core starter stacks[/bold]\n")
    print(f"Using model: [bold]{model}[/bold]")
    print("Override with --model or set PERSONALITY_CORE_DEFAULT_MODEL.\n")
    for name, core_spec, prompt_text in examples:
        print(f"[bold]{name}[/bold]")
        print(f'personality-core chat "{prompt_text}" --model "{model}" --cores "{core_spec}" --max-tokens 300 --debug')
        print()
    print("After the fast path works, add --stabilizer to test drift repair.")

async def run_request(req: ChatCompletionRequest) -> dict:
    return await PersonalityPipeline(DEFAULT_CORES_DIR, DEFAULT_PERSONALITIES_DIR, DEFAULT_MODEL_PROFILES_DIR).run(req)

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
