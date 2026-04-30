# Personality Core

Runtime behavior control for LLM applications.

Personality Core is an OpenAI-compatible middleware layer that lets teams define, stack, validate, and repair model behavior at runtime. It started with Portal-inspired personality modules, but the core abstraction is broader: a stackable behavior contract for agents and LLM pipelines.

Use it to keep long-running assistants, agent chains, and tool pipelines closer to the behavior you intended:

- consistent voice and tone
- structured JSON output
- provider-independent model routing
- drift evaluation and repair
- inspectable prompt compilation
- stackable behavior presets for different workflows

```text
request -> core stack -> compiled behavior contract -> model -> evaluator -> optional repair -> response
```

## Why This Exists

LLM behavior drifts. A model can start in the right voice, then slowly become generic. It can return prose where a downstream node expects JSON. It can grow verbose, lose skepticism, soften constraints, or ignore a carefully written system prompt after enough context pressure.

Personality Core gives that behavior a runtime layer:

1. Define behavior as declarative JSON cores.
2. Stack cores per request or preset.
3. Compile the stack into model-specific instructions.
4. Call the selected provider.
5. Evaluate whether the output matched the stack.
6. Warn, repair, block, or return raw output when contracts fail.

The goal is not to pretend the model has a stable inner personality. The goal is to make outward behavior observable, repeatable, and enforceable enough for real agent workflows.

## Current Capabilities

- FastAPI server with OpenAI-compatible `/v1/chat/completions`
- provider routing for Ollama, OpenAI, OpenRouter, and LM Studio-style endpoints
- declarative JSON core registry
- stack resolver with trait merging, rules, boundaries, conflicts, and contracts
- model-specific prompt compiler
- heuristic style evaluator
- behavior contract evaluator
- optional stabilizer/repair pass
- CLI for local inspection and demos
- React workbench for stack editing, provider testing, comparison, and core creation
- model-assisted core drafting through the selected runtime model

## Install

```bash
git clone https://github.com/SEsquieu/personality-core.git
cd personality-core

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

npm install
```

On macOS/Linux, activate the venv with:

```bash
source .venv/bin/activate
```

## Quickstart With Ollama

Start Ollama and pull a chat model:

```bash
ollama serve
ollama pull gemma4:e4b
```

Start the Personality Core API:

```bash
personality-core serve --host 127.0.0.1 --port 8787
```

In another terminal, start the workbench:

```bash
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

In the Runtime panel, click `Test Provider`. If Ollama responds, run a stack or draft a core.

## Terminal Demo

Run the same prompt through saved behavior stacks:

```bash
personality-core compare --demo retry_loop --model "ollama/gemma4:e4b" --max-tokens 260
```

Run a custom stack:

```bash
personality-core chat "Explain why hiding errors behind retries makes debugging miserable." `
  --model "ollama/gemma4:e4b" `
  --cores "technical_core:0.95,sarcasm_core:0.7,low_verbosity_core:0.75" `
  --max-tokens 300 `
  --debug
```

PowerShell uses backticks for line continuation. In bash/zsh, use `\`.

## OpenAI-Compatible Usage

Point an existing OpenAI client at the local proxy and pass cores in `extra_body`.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="ollama/gemma4:e4b",
    messages=[{"role": "user", "content": "Why is config drift a problem?"}],
    extra_body={
        "cores": [
            {"id": "technical_core", "strength": 0.9},
            {"id": "skepticism_core", "strength": 0.7},
            {"id": "stability_core", "strength": 0.8}
        ],
        "stabilizer": {"enabled": True},
        "fail_policy": "repair",
        "debug": True
    }
)

print(response.choices[0].message.content)
```

## Behavior Contracts

Cores can be personality modules, but they can also be operational contracts. The built-in `structured_json_output_core` requires the model to return one valid JSON object with:

```json
{
  "answer": "string",
  "confidence": 0.86,
  "notes": ["short validation notes"]
}
```

Example request:

```json
{
  "model": "ollama/gemma4:e4b",
  "messages": [
    {
      "role": "user",
      "content": "Summarize why retries hide real errors."
    }
  ],
  "cores": [
    { "id": "structured_json_output_core", "strength": 1.0 },
    { "id": "technical_core", "strength": 0.8 }
  ],
  "fail_policy": "repair",
  "debug": true
}
```

Contract fail policies:

- `warn`: return the output and include contract warnings
- `repair`: ask the model to repair contract drift
- `block`: return no content when the contract fails
- `raw`: return the raw model output

See [docs/behavior_contracts.md](docs/behavior_contracts.md).

## Provider Routing

Model prefixes select the provider:

```text
ollama/gemma4:e4b                  -> Ollama
gemma4:e4b                         -> Ollama shorthand
openai/gpt-4.1-mini                -> OpenAI
openrouter/openai/gpt-4o-mini      -> OpenRouter
lmstudio/local-model               -> LM Studio local server
```

Copy `.env.example` to `.env` and set provider keys as needed. The workbench also exposes `GET /v1/providers` metadata through the Runtime panel.

See [docs/provider_setup.md](docs/provider_setup.md).

## Core Files

Cores are declarative JSON files in `cores/`.

```json
{
  "id": "skepticism_core",
  "name": "Skepticism Core",
  "kind": "personality",
  "trait_deltas": {
    "skepticism": 0.9,
    "directness": 0.4,
    "agreeableness": -0.4
  },
  "default_strength": 0.75,
  "rules": [
    "Challenge weak assumptions directly.",
    "Do not agree just to be agreeable.",
    "Explain what could break or be missing."
  ],
  "boundaries": {
    "preserve_task_accuracy": true,
    "no_fake_certainty": true
  }
}
```

The workbench includes a Core Creator that can:

- load a valid template
- draft a core with the selected model
- validate schema and ranges
- install the core into `cores/`
- add it to the active stack

See [docs/core_creator.md](docs/core_creator.md).

## Workbench

The React workbench is designed for interactive development:

- **Stack Editor**: add cores, tune strengths, resolve, compile, run
- **Compare**: run the same prompt through saved presets
- **Core Creator**: draft and validate new cores
- **Runtime**: choose provider model, test provider, choose contract fail policy
- **Diagnostics**: inspect resolved traits, core scores, conflicts, contracts, and trace

See [docs/frontend_workbench.md](docs/frontend_workbench.md).

## CLI Reference

```bash
personality-core list-cores
personality-core inspect structured_json_output_core
personality-core validate cores/structured_json_output_core.json
personality-core stack --cores technical_core:0.9,skepticism_core:0.7
personality-core prompt --cores technical_core:0.9,structured_json_output_core:1.0
personality-core demo
personality-core chat "Why is config drift a problem?" --cores technical_core:0.9,skepticism_core:0.7 --debug
personality-core compare --demo retry_loop --summary
personality-core test --model ollama/gemma4:e4b --cores technical_core:0.95,sarcasm_core:0.7 --turns 3
```

## API Routes

Native routes:

- `GET /health`
- `GET /v1/cores`
- `GET /v1/cores/template`
- `POST /v1/cores/draft`
- `POST /v1/cores/validate`
- `POST /v1/cores/install`
- `GET /v1/personalities`
- `GET /v1/providers`
- `POST /v1/providers/health`
- `POST /v1/stack/resolve`
- `POST /v1/stack/compile`
- `POST /v1/stack/run`
- `POST /v1/compare`

Compatibility route:

- `POST /v1/chat/completions`

## Architecture

```text
Application / Agent
        |
        v
OpenAI-compatible proxy
        |
        v
Core registry + stack resolver
        |
        v
Prompt compiler + provider adapter
        |
        v
LLM provider
        |
        v
Style evaluator + contract evaluator
        |
        v
Fail policy + optional stabilizer
        |
        v
Response + debug metadata
```

## Project Status

This is an active MVP. The core architecture is in place, including provider routing, stack resolution, behavior contracts, and repair policy. It is ready for local experimentation and early integration work, but it is not production hardened yet.

Near-term priorities:

- richer contract types
- stronger evaluator plugins
- saved custom stacks
- SDK helpers for common agent frameworks
- persisted run history and regression tests
- provider-specific streaming support

## Documentation

- [Provider setup](docs/provider_setup.md)
- [Behavior contracts](docs/behavior_contracts.md)
- [Core creator](docs/core_creator.md)
- [Stack workflow](docs/stack_workflow.md)
- [Frontend workbench](docs/frontend_workbench.md)
- [Demo kit](docs/demo_kit.md)
