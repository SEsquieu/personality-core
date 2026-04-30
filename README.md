# Personality Core

Composable personality cores for LLMs. Tune, stack, evaluate, and stabilize model behavior across long-running conversations and agent loops.

Inspired by modular personality cores from *Portal*, but built as practical LLM infrastructure.

```txt
Install cores.
Tune cores.
Stack cores.
Stabilize cores.
```

## What this is

Personality Core is an OpenAI-compatible local proxy. It accepts normal `/v1/chat/completions` requests, composes a stack of declarative JSON personality cores, compiles them into model-specific instructions, calls an LLM runtime such as Ollama, evaluates style alignment, and optionally runs a stabilizer pass to repair drift.

The transport stays boring. The interface gets the fun.

## Quickstart

### 1. Install

```bash
cd personality-core
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
npm install
```

### 2. Choose a model backend

Ollama works out of the box:

```bash
ollama serve
ollama pull gemma4:e4b
```

Any Ollama chat model should work. Use the `ollama/` prefix when passing it to Personality Core:

```bash
personality-core chat "Why is config drift a problem?" --model "ollama/gemma4:e4b"
```

You can set a different default model:

```bash
PERSONALITY_CORE_DEFAULT_MODEL=ollama/llama3.2:3b
```

### 3. Run Personality Core

```bash
personality-core serve --host 127.0.0.1 --port 8787
```

### 4. Try a personality stack from the terminal

```bash
personality-core demo
```

Then run one of the printed examples, or try:

```bash
personality-core chat "Explain why hiding errors behind retries makes debugging miserable." \
  --model "ollama/gemma4:e4b" \
  --cores "technical_core:0.95,sarcasm_core:0.7,profanity_core:0.35,low_verbosity_core:0.75" \
  --max-tokens 300 \
  --debug
```

Personality Core sends `think: false` to Ollama by default so thinking-capable models use the token budget for visible output. Pass `--think` if you want Ollama reasoning traces enabled.

If the output stops mid-sentence or mid-list, increase `--max-tokens`. Debug mode includes `model_response.done_reason`; `length` means the model hit the output cap.

Once the fast path works, add `--stabilizer` to test the optional repair pass.

### 5. Compare personalities

Run the same prompt through several saved personality presets:

```bash
personality-core compare "Explain why retries hide real errors." \
  --model "ollama/gemma4:e4b" \
  --max-tokens 260
```

This is the fastest way to see the core stack idea in motion: same model, same prompt, different resolved behavior.

Named demo prompts are built in:

```bash
personality-core compare --demo retry_loop --summary
personality-core compare --demo angry_customer --json
personality-core compare --demo code_review --save runs/code-review-demo.json
```

Available demos: `retry_loop`, `angry_customer`, `code_review`, `startup_pitch`, `debugging`.

### 6. Test the OpenAI-compatible endpoint

```bash
curl http://127.0.0.1:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/gemma4:e4b",
    "messages": [
      {"role": "user", "content": "Explain why mutating shared state inside a retry loop is dangerous."}
    ],
    "cores": [
      {"id": "technical_core", "strength": 0.95},
      {"id": "sarcasm_core", "strength": 0.7},
      {"id": "profanity_core", "strength": 0.35},
      {"id": "low_verbosity_core", "strength": 0.75}
    ],
    "stabilizer": {"enabled": true, "threshold": 0.78},
    "debug": true
  }'
```

### 7. Run the workbench UI

Start the API:

```bash
personality-core serve --host 127.0.0.1 --port 8787
```

Start the Vite app:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The workbench loads cores and personality presets from the API. The default Stack Editor lets you install cores, tune strengths, resolve the stack, compile the stack prompt, and run the active stack. Compare mode remains available for side-by-side preset demos.

Core Creator mode starts with a valid JSON template, can draft a schema-valid core from a plain-language behavior intent through the selected model endpoint, lets you edit the JSON, validates it, installs it into `cores/`, and adds it to the active stack.

Use the Runtime panel to pick a provider model and run `Test Provider` before running a stack. Supported model prefixes include `ollama/`, bare Ollama model names, `openai/`, `openrouter/`, and `lmstudio/`. See [docs/provider_setup.md](docs/provider_setup.md).

Behavior contracts let cores enforce output requirements such as valid JSON, then warn, repair, block, or return raw output when the model drifts. The first built-in contract core is `structured_json_output_core`. See [docs/behavior_contracts.md](docs/behavior_contracts.md).

## Python client example

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="ollama/gemma4:e4b",
    messages=[{"role": "user", "content": "Why is config drift a problem?"}],
    extra_body={
        "cores": [
            {"id": "technical_core", "strength": 0.9},
            {"id": "sarcasm_core", "strength": 0.65},
            {"id": "stability_core", "strength": 0.8},
        ],
        "stabilizer": {"enabled": True},
    },
)

print(response.choices[0].message.content)
```

## CLI

```bash
personality-core list-cores
personality-core inspect sarcasm_core
personality-core validate cores/sarcasm_core.json
personality-core stack --cores technical_core:0.9,sarcasm_core:0.7,profanity_core:0.3
personality-core prompt --cores technical_core:0.9,sarcasm_core:0.7
personality-core demo
personality-core chat "Why is config drift a problem?" --cores technical_core:0.9,sarcasm_core:0.65 --debug
personality-core compare "Explain retry loops like I am debugging production."
personality-core compare --demo code_review --summary
personality-core compare --demo retry_loop --json
personality-core test --model ollama/gemma4:e4b --cores technical_core:0.95,sarcasm_core:0.7 --turns 3
npm run dev
npm run build
```

## Configuration

By default, the CLI and server load local assets from `cores/`, `personalities/`, and `model_profiles/`.

You can override those paths when embedding Personality Core in another project:

```bash
PERSONALITY_CORE_CORES_DIR=/path/to/cores
PERSONALITY_CORE_PERSONALITIES_DIR=/path/to/personalities
PERSONALITY_CORE_MODEL_PROFILES_DIR=/path/to/model_profiles
PERSONALITY_CORE_DEFAULT_MODEL=ollama/gemma4:e4b
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT=300
OPENAI_API_KEY=
```

## Core files

Cores are declarative JSON files in `cores/`.

```json
{
  "id": "sarcasm_core",
  "name": "Sarcasm Core",
  "trait_deltas": {
    "sarcasm": 0.8,
    "formality": -0.2,
    "warmth": -0.1
  },
  "default_strength": 0.65,
  "rules": [
    "Use dry sarcasm when pointing out obvious mistakes.",
    "Do not aim sarcasm at the user personally.",
    "Preserve technical accuracy over comedic timing."
  ]
}
```

A request installs cores into the active stack:

```json
{
  "cores": [
    {"id": "technical_core", "strength": 0.9},
    {"id": "sarcasm_core", "strength": 0.7}
  ]
}
```

## Architecture

```txt
App / Agent
   ↓
Personality Core proxy
   ↓
Core registry + stack resolver
   ↓
Core compiler
   ↓
Model adapter
   ↓
LLM runtime
   ↓
Evaluator
   ↓
Optional stabilizer
   ↓
OpenAI-compatible response
```

## Current status

This is an MVP scaffold intended for tinkering:

- FastAPI server
- OpenAI-compatible `/v1/chat/completions`
- Ollama adapter
- core registry and validation
- stack resolver
- model profiles
- compiler
- heuristic evaluator
- optional LLM-powered stabilizer pass
- CLI
- default cores and presets

Not production hardened yet.
