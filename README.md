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

### 5. Test the OpenAI-compatible endpoint

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
personality-core test --model ollama/gemma4:e4b --cores technical_core:0.95,sarcasm_core:0.7 --turns 3
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
