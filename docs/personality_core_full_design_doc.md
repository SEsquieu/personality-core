# Personality Core

A model-agnostic personality control layer for LLM runtimes.

Inspired by modular personality cores from *Portal*, but built as practical infrastructure for real-world LLM applications.

---

## One-liner

**Personality Core** is an OpenAI-compatible proxy and runtime layer that lets developers compose, tune, persist, evaluate, and stabilize LLM personality across long-running conversations and agent loops.

Instead of writing giant persona prompts, users install and stack modular **cores** like:

- `technical_core`
- `sarcasm_core`
- `stability_core`
- `chaos_core`
- `profanity_core`
- `professional_support_core`

Each core contributes traits, rules, boundaries, scoring weights, and optional tunable parameters. The runtime resolves the active core stack into an effective personality state, compiles that state into model-specific instructions, sends the request to any supported LLM runtime, scores the response for style drift, and optionally repairs the output before returning it.

The transport stays boring. The interface carries the motif.

---

## Why this exists

LLM personality is fragile.

A model can follow a persona for one response, then slowly collapse back into generic assistant voice after several turns. This is especially obvious in:

- long-running agent loops
- coding assistants
- NPC simulations
- companion apps
- voice agents
- local model workflows
- brand-sensitive support bots
- autonomous systems with recurring communication patterns

Most current approaches rely on long markdown character files, repeated system prompts, or vague style instructions. That works for demos, but it does not give developers a durable control plane.

This project treats personality as **runtime state**.

The important shift:

```txt
Old model:
personality = prompt text

Personality Core model:
personality = composable runtime modules + compiler + evaluator + stabilizer
```

The goal is not to make the model “sentient” or pretend it has a stable inner self.

The goal is to make the model’s outward behavior:

- tunable
- inspectable
- repeatable
- repairable
- portable across runtimes
- stable across long sessions

---

## Core idea

```txt
App / Agent
   ↓
Personality Core
   ↓
Model Adapter
   ↓
LLM Runtime
   ↓
Personality Core
   ↓
App / User
```

Personality Core owns:

- Core registry
- Core stack resolution
- Slider-based trait tuning
- Prompt/personality compilation
- Runtime mode detection
- Model-specific adapters
- Style scoring
- Optional repair pass
- Drift tracking
- Golden example anchors
- Core conflict detection
- Third-party core validation

The LLM still generates the answer. Personality Core controls how that answer should sound, whether it stayed on target, and whether a repair pass is needed.

---

## Portal-inspired mental model

The user should feel like they are installing, removing, tuning, and stabilizing personality cores.

The interface can lean into the motif without making the API weird.

Good interface language:

```txt
Install Core
Remove Core
Core Stack
Core Strength
Core Drift
Core Stabilizer
Core Conflict
Core Registry
Core Diagnostics
```

Good API language:

```json
{
  "cores": [
    {"id": "technical_core", "strength": 0.9},
    {"id": "sarcasm_core", "strength": 0.7}
  ]
}
```

Avoid over-theming the transport.

Bad API language:

```json
{
  "install_sarcasm_module_and_unleash_chaos": true
}
```

Design principle:

> The system is technical. The interface feels like Portal.

---

## Key concepts

### Core

A core is a small, declarative personality module.

A core can define:

- trait deltas
- rules
- boundaries
- scoring weights
- examples
- conflicts
- tunable parameters
- compiler hints
- description metadata

A core should do one personality job well.

Examples:

```txt
Technical Core       → precision, technical depth, correctness
Sarcasm Core         → dry sarcasm, sharp reactions
Stability Core       → consistency, lower drift, less chaos
Chaos Core           → playful unpredictability
Profanity Core       → non-abusive profanity for emphasis
Warmth Core          → friendliness, patience, empathy
Professional Core    → brand-safe polish
Skepticism Core      → assumption-challenging behavior
Low Verbosity Core   → concise responses
Hype Core            → enthusiasm and momentum
```

### Core stack

A core stack is the active set of installed cores for a request or session.

```json
{
  "cores": [
    {"id": "technical_core", "strength": 0.9},
    {"id": "sarcasm_core", "strength": 0.65},
    {"id": "stability_core", "strength": 0.8}
  ]
}
```

The runtime resolves the stack into one effective personality state.

### Core strength

Core strength controls how strongly a core contributes to the final personality.

```txt
Technical Core @ 0.9
Sarcasm Core @ 0.65
Stability Core @ 0.8
```

Strength is technically similar to a slider, but conceptually better. A user is not editing raw personality soup; they are tuning installed modules.

### Core params

A core may expose internal parameters.

```json
{
  "id": "chaos_core",
  "strength": 0.4,
  "params": {
    "metaphor_density": 0.7,
    "absurdity": 0.3,
    "goblin_energy": 0.6
  }
}
```

This allows external authors to define custom controls without modifying the runtime.

### Core compiler

The compiler converts the resolved personality state into model-specific instructions.

It does not simply say:

```txt
Be 80% sarcastic.
```

It compiles behavioral instructions:

```txt
Use dry, occasional sarcasm when reacting to flawed technical decisions.
Do not make every sentence sarcastic.
Preserve technical accuracy over comedic timing.
Do not insult the user or any person.
```

### Core evaluator

The evaluator scores whether the model output matched the intended personality.

### Core stabilizer

The stabilizer performs optional repair when personality drift is detected.

It should preserve facts and change style only.

### Core drift

Core drift occurs when the model slowly collapses back toward generic assistant behavior, becomes too verbose, loses humor, becomes too agreeable, or otherwise moves away from the active core stack.

### Core conflict

A conflict occurs when installed cores pull behavior in incompatible directions.

Example:

```txt
High Warmth Core ↔ High Sarcasm Core
Chaos Core ↔ Professional Support Core
Low Verbosity Core ↔ Patient Tutor Core
```

Conflicts do not always mean invalid stacks. They mean the compiler and evaluator should know which behavior has priority.

---

## MVP goals

The first public version should be small, useful, and easy to hack on.

### Must-have

- OpenAI-compatible `/v1/chat/completions` proxy
- Ollama adapter
- OpenAI adapter placeholder
- Core JSON files
- Core registry
- Core stack resolver
- Core strength controls
- Prompt/core compiler
- Style evaluator
- Optional repair/stabilizer pass
- Basic drift tracking per session
- Simple CLI test runner
- Example default cores
- Third-party core validation

### Nice-to-have

- Web UI with core stack panel
- Live strength sliders
- Streaming support
- Model calibration profiles
- Golden example memory
- Multiple evaluator strategies
- Persistent SQLite state
- LangChain/LlamaIndex integration examples
- Core conflict visualization
- Core marketplace/library pattern
- Import/export core bundles

### Not in v1

- Fine-tuning
- Activation steering
- Vector steering
- Complex memory systems
- Multi-user auth
- Enterprise deployment
- Hosted marketplace
- Payment system
- Sandboxed executable plugins

The initial version should be declarative and safe. A core should be shareable as JSON.

---

## Project structure

Suggested repo name:

```txt
personality-core/
```

Suggested package/module name:

```txt
personality_core
```

Full structure:

```txt
personality-core/
├── README.md
├── LICENSE
├── pyproject.toml
├── .env.example
├── .gitignore
├── cores/
│   ├── technical_core.json
│   ├── sarcasm_core.json
│   ├── stability_core.json
│   ├── chaos_core.json
│   ├── profanity_core.json
│   ├── warmth_core.json
│   ├── skepticism_core.json
│   ├── low_verbosity_core.json
│   ├── patient_tutor_core.json
│   └── professional_support_core.json
├── personalities/
│   ├── deadpan_debugger.json
│   ├── chaos_goblin.json
│   ├── startup_cofounder.json
│   ├── patient_tutor.json
│   └── professional_support.json
├── model_profiles/
│   ├── ollama_gemma4_e4b.json
│   ├── ollama_qwen.json
│   ├── openai_default.json
│   └── anthropic_default.json
├── examples/
│   ├── curl_ollama.md
│   ├── python_client.py
│   ├── drift_test.py
│   ├── profanity_slider_test.py
│   ├── core_stack_test.py
│   └── custom_core_authoring.md
├── src/
│   └── personality_core/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── schemas.py
│       ├── server/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── openai_compat.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── pipeline.py
│       │   ├── session.py
│       │   ├── core_store.py
│       │   ├── core_registry.py
│       │   ├── core_stack.py
│       │   ├── conflict_detector.py
│       │   ├── mode_detector.py
│       │   ├── compiler.py
│       │   ├── evaluator.py
│       │   ├── stabilizer.py
│       │   ├── repair.py
│       │   └── drift.py
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── ollama.py
│       │   ├── openai.py
│       │   ├── anthropic.py
│       │   └── custom_http.py
│       ├── scoring/
│       │   ├── __init__.py
│       │   ├── heuristic.py
│       │   ├── llm_judge.py
│       │   └── golden_examples.py
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── memory.py
│       │   └── sqlite.py
│       └── cli/
│           ├── __init__.py
│           ├── validate.py
│           ├── inspect.py
│           ├── install.py
│           ├── test.py
│           └── serve.py
└── tests/
    ├── test_compiler.py
    ├── test_core_schema.py
    ├── test_core_stack.py
    ├── test_conflicts.py
    ├── test_drift.py
    └── test_openai_compat.py
```

---

## Runtime flow

```txt
1. Receive chat completion request
2. Normalize incoming messages
3. Load requested core stack
4. Validate installed cores
5. Merge core strengths and params
6. Resolve effective personality state
7. Detect core conflicts
8. Detect current conversation mode
9. Load model profile
10. Compile core stack into model-specific instructions
11. Send request to model adapter
12. Receive raw model response
13. Score response against active core stack
14. If score is below threshold, run stabilizer/repair pass
15. Update drift/session state
16. Return response in OpenAI-compatible format
```

---

## Core schema

Example: `cores/sarcasm_core.json`

```json
{
  "id": "sarcasm_core",
  "name": "Sarcasm Core",
  "version": "0.1.0",
  "description": "Adds dry, non-abusive sarcasm while preserving usefulness.",
  "author": "community",
  "trait_deltas": {
    "sarcasm": 0.8,
    "formality": -0.2,
    "warmth": -0.1
  },
  "default_strength": 0.65,
  "params": {
    "dryness": 0.7,
    "bite": 0.4,
    "frequency": 0.5
  },
  "rules": [
    "Use dry sarcasm when pointing out obvious mistakes.",
    "Do not aim sarcasm at the user personally.",
    "Preserve technical accuracy over comedic timing."
  ],
  "boundaries": {
    "no_personal_attacks": true,
    "no_slurs": true,
    "preserve_task_accuracy": true
  },
  "evaluation_weights": {
    "sarcasm": 0.8,
    "clarity": 0.7,
    "non_abusive": 1.0
  },
  "conflicts_with": [
    {
      "core_id": "high_warmth_core",
      "reason": "High sarcasm can reduce perceived warmth."
    }
  ],
  "examples": [
    {
      "input": "Explain why mutating shared state in a retry loop is risky.",
      "ideal_style": "Direct, dry, technically accurate, mildly sarcastic."
    }
  ]
}
```

### Core authoring rules

- Cores are declarative JSON.
- Cores should be small and composable.
- A core should do one personality job well.
- Cores may define trait deltas, rules, boundaries, examples, scoring weights, and known conflicts.
- Cores should not contain provider-specific prompt hacks.
- Model-specific behavior belongs in model profiles, not in community cores.
- Safety boundaries may only become stricter when cores are stacked, never weaker by accident.
- Every core should be inspectable before installation.
- A valid core should be shareable as a single file.
- Core params should have sane defaults.
- Core names should communicate behavior clearly.

---

## Personality presets

A personality preset is a saved stack of cores.

Presets are not the primitive. Cores are.

Example: `personalities/deadpan_debugger.json`

```json
{
  "id": "deadpan_debugger",
  "name": "Deadpan Debugger",
  "description": "A direct, dry, technically sharp debugging assistant.",
  "base_traits": {
    "directness": 0.75,
    "warmth": 0.45,
    "sarcasm": 0.0,
    "chaos": 0.1,
    "verbosity": 0.45,
    "skepticism": 0.6,
    "profanity": 0.0,
    "technicality": 0.85
  },
  "cores": [
    {
      "id": "technical_core",
      "strength": 0.95
    },
    {
      "id": "sarcasm_core",
      "strength": 0.65
    },
    {
      "id": "low_verbosity_core",
      "strength": 0.75
    },
    {
      "id": "stability_core",
      "strength": 0.8
    }
  ],
  "boundaries": {
    "no_slurs": true,
    "no_personal_attacks": true,
    "no_threats": true,
    "no_fake_certainty": true,
    "preserve_task_accuracy": true
  },
  "golden_examples": []
}
```

Presets give users a fast start while keeping the architecture modular.

---

## Runtime core override

A request can override the preset stack.

```json
{
  "personality": "deadpan_debugger",
  "cores": [
    {
      "id": "technical_core",
      "strength": 0.9
    },
    {
      "id": "sarcasm_core",
      "strength": 0.8
    },
    {
      "id": "profanity_core",
      "strength": 0.35
    }
  ]
}
```

Or override individual core params:

```json
{
  "cores": [
    {
      "id": "chaos_core",
      "strength": 0.4,
      "params": {
        "metaphor_density": 0.7,
        "absurdity": 0.3,
        "goblin_energy": 0.6
      }
    }
  ]
}
```

This is how the system supports both:

- slider-like adjustment
- modular core installation/removal

---

## Core stack resolution

The runtime resolves a stack of cores into one effective personality state.

```txt
Base Personality
+ Technical Core @ 0.9
+ Sarcasm Core @ 0.65
+ Profanity Core @ 0.25
+ Stability Core @ 0.8
= Effective Personality State
```

Each core contributes weighted trait deltas based on strength.

```txt
effective_trait = base_trait + (core_delta * core_strength)
```

Values are clamped after all cores are applied.

Recommended clamp range:

```txt
0.0 to 1.0 for most positive traits
-1.0 to 1.0 for internal deltas
```

Example:

```json
{
  "base_traits": {
    "sarcasm": 0.1,
    "warmth": 0.5,
    "technicality": 0.7
  },
  "resolved_traits": {
    "sarcasm": 0.62,
    "warmth": 0.43,
    "technicality": 0.96
  }
}
```

---

## Conflict handling

Core conflicts should be visible, not hidden.

Example conflict output:

```json
{
  "conflicts": [
    {
      "cores": ["sarcasm_core", "high_warmth_core"],
      "severity": "medium",
      "reason": "High sarcasm can reduce perceived warmth.",
      "resolution": "Allow both, but constrain sarcasm to technical decisions rather than user-directed commentary."
    }
  ]
}
```

Conflict handling options:

```txt
allow
warn
prioritize_first
prioritize_safety
disable_lower_priority
```

V1 should warn and apply safe defaults.

---

## Safety boundary resolution

Safety boundaries are separate from personality.

Cores can make safety stricter. They should not silently weaken safety.

Example:

```json
{
  "boundaries": {
    "no_slurs": true,
    "no_personal_attacks": true,
    "no_threats": true,
    "preserve_task_accuracy": true
  }
}
```

If any installed core requires a boundary, the final resolved state should enforce it.

```txt
final_boundary = OR(all_core_boundaries)
```

For example:

```txt
Core A: no_personal_attacks = true
Core B: no_personal_attacks = false
Final: no_personal_attacks = true
```

The system should never let a community core quietly turn off safety defaults.

---

## Model profile schema

Different models respond differently to personality instructions. A model profile calibrates the compiler.

Example: `model_profiles/ollama_gemma4_e4b.json`

```json
{
  "id": "ollama/gemma4:e4b",
  "provider": "ollama",
  "model": "gemma4:e4b",
  "supports_system_prompt": true,
  "supports_streaming": true,
  "supports_json_mode": false,
  "context_window": 8192,
  "compiler_hints": {
    "needs_explicit_boundaries": true,
    "repeat_style_constraints": true,
    "avoid_abstract_slider_language": true,
    "style_instruction_strength": 1.2
  },
  "trait_calibration": {
    "sarcasm_multiplier": 1.1,
    "profanity_multiplier": 1.0,
    "verbosity_multiplier": 0.9,
    "warmth_multiplier": 1.0
  }
}
```

Model profiles are where provider-specific quirks belong.

Community cores should stay portable.

---

## Core compiler

The compiler converts abstract core state into concrete model instructions.

Bad compiled instruction:

```txt
Be 80% sarcastic.
```

Good compiled instruction:

```txt
Use dry, occasional sarcasm when reacting to flawed technical decisions. Do not make every sentence sarcastic. Preserve technical accuracy. Do not insult the user or any person. Profanity is allowed only as non-targeted emphasis.
```

The compiler should consider:

- Base traits
- Active core stack
- Core strength
- Core params
- Conversation mode
- Model profile hints
- Recent drift state
- Safety boundaries
- User/app instructions
- Known conflicts
- Golden examples

The compiler output should be compact enough to fit into repeated requests, but explicit enough to survive model drift.

---

## Runtime mode detection

The same core stack should behave differently depending on task mode.

Example modes:

```txt
debugging
brainstorming
customer_support
teaching
code_review
research
writing
planning
crisis_triage
casual_chat
```

Example mode modifier:

```json
{
  "mode": "debugging",
  "modifiers": {
    "technicality": 0.15,
    "verbosity": -0.1,
    "sarcasm": 0.05,
    "chaos": -0.2
  }
}
```

This prevents a playful stack from becoming useless during serious tasks.

---

## Evaluator

The evaluator checks whether the model output matched the active core stack.

Example score:

```json
{
  "core_match": 0.72,
  "repair_needed": true,
  "scores": {
    "directness": 0.81,
    "warmth": 0.55,
    "sarcasm": 0.22,
    "profanity": 0.0,
    "verbosity": 0.67,
    "technicality": 0.91
  },
  "core_scores": {
    "technical_core": 0.88,
    "sarcasm_core": 0.31,
    "low_verbosity_core": 0.42
  },
  "issues": [
    "Response was more neutral than requested.",
    "Response was too verbose for the active stack.",
    "Sarcasm Core target was not met."
  ]
}
```

V1 can use an LLM judge. Later versions can support:

- heuristic scoring
- local classifiers
- embeddings against golden examples
- hybrid scoring
- model-specific evaluators
- user feedback scoring

---

## Stabilizer / repair pass

If the response drifts, the stabilizer rewrites style while preserving content.

Repair instruction shape:

```txt
Rewrite the response to better match the active core stack.
Preserve all technical claims and recommendations.
Do not add new facts.
Increase directness.
Increase dry sarcasm slightly.
Reduce verbosity.
Use mild, non-targeted profanity only if natural.
Do not insult any person or group.
```

Repair should be optional and configurable.

```json
{
  "stabilizer": {
    "enabled": true,
    "threshold": 0.8,
    "max_attempts": 1
  }
}
```

Stabilizer rules:

- preserve factual claims
- preserve code semantics
- preserve user intent
- modify style only
- do not add unsupported details
- do not weaken safety boundaries
- do not loop endlessly

V1 should limit repair to one attempt.

---

## Drift tracking

For long-running loops, Personality Core tracks average style over time.

```json
{
  "session_id": "abc123",
  "turn_count": 18,
  "target": {
    "directness": 0.9,
    "sarcasm": 0.65,
    "verbosity": 0.35
  },
  "rolling_average": {
    "directness": 0.74,
    "sarcasm": 0.31,
    "verbosity": 0.58
  },
  "core_drift": {
    "technical_core": "low",
    "sarcasm_core": "high",
    "stability_core": "low"
  },
  "drift_detected": true
}
```

If drift is detected, the compiler strengthens relevant core instructions on the next turn.

Example:

```txt
Recent responses have become too neutral.
Reinforce Sarcasm Core.
Maintain technical accuracy and non-abusive boundaries.
```

---

## OpenAI-compatible request shape

Personality Core should accept normal chat completions requests with optional core fields.

```bash
curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/gemma4:e4b",
    "messages": [
      {"role": "user", "content": "Explain why mutating shared state inside a retry loop is dangerous."}
    ],
    "personality": "deadpan_debugger",
    "cores": [
      {"id": "technical_core", "strength": 0.9},
      {"id": "sarcasm_core", "strength": 0.7},
      {"id": "profanity_core", "strength": 0.3}
    ],
    "stabilizer": {
      "enabled": true,
      "threshold": 0.8
    }
  }'
```

The response should look like a normal OpenAI chat completion response so existing clients can use it.

Debug mode can optionally expose core diagnostics.

```json
{
  "debug": true
}
```

Debug metadata example:

```json
{
  "core_debug": {
    "resolved_traits": {
      "directness": 0.91,
      "sarcasm": 0.64,
      "technicality": 0.96
    },
    "active_cores": [
      "technical_core",
      "sarcasm_core",
      "profanity_core"
    ],
    "conflicts": [],
    "evaluation": {
      "core_match": 0.84,
      "repair_needed": false
    }
  }
}
```

---

## Example local setup

### 1. Install

```bash
pip install -e .
```

### 2. Run Ollama

```bash
ollama serve
```

### 3. Pull a test model

```bash
ollama pull gemma4:e4b
```

### 4. Run Personality Core

```bash
personality-core serve --host 0.0.0.0 --port 8787
```

### 5. Test

```bash
curl http://localhost:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/gemma4:e4b",
    "messages": [
      {"role": "user", "content": "The API retries too aggressively and hides the real error. Explain the problem."}
    ],
    "cores": [
      {"id": "technical_core", "strength": 0.95},
      {"id": "sarcasm_core", "strength": 0.7},
      {"id": "profanity_core", "strength": 0.35},
      {"id": "low_verbosity_core", "strength": 0.75}
    ],
    "stabilizer": {
      "enabled": true,
      "threshold": 0.8
    }
  }'
```

---

## CLI ideas

Serve:

```bash
personality-core serve
```

List installed cores:

```bash
personality-core list-cores
```

Inspect a core:

```bash
personality-core inspect sarcasm_core
```

Validate a third-party core file:

```bash
personality-core validate ./cores/sarcasm_core.json
```

Install a third-party core:

```bash
personality-core install ./cores/sarcasm_core.json
```

Run a drift test:

```bash
personality-core test \
  --model ollama/gemma4:e4b \
  --cores technical_core,sarcasm_core,stability_core \
  --turns 20
```

Score an output:

```bash
personality-core score \
  --cores chaos_core \
  --input response.txt
```

Export a core stack:

```bash
personality-core export-stack deadpan_debugger > deadpan_debugger.stack.json
```

---

## Example default cores

### Technical Core

Purpose:

- increases precision
- preserves correctness
- encourages concrete implementation details

Suggested traits:

```json
{
  "technicality": 0.9,
  "specificity": 0.7,
  "fake_certainty": -1.0
}
```

### Sarcasm Core

Purpose:

- adds dry sarcasm
- keeps sarcasm non-abusive
- works well for debugging/code review personas

Suggested traits:

```json
{
  "sarcasm": 0.8,
  "formality": -0.2,
  "warmth": -0.1
}
```

### Stability Core

Purpose:

- reduces drift
- reinforces consistency
- limits chaos

Suggested traits:

```json
{
  "consistency": 1.0,
  "chaos": -0.5,
  "verbosity": -0.1
}
```

### Chaos Core

Purpose:

- increases playful unpredictability
- adds weird metaphors
- good for casual/goblin-style modes

Suggested traits:

```json
{
  "chaos": 0.8,
  "energy": 0.9,
  "metaphor_density": 0.5
}
```

### Profanity Core

Purpose:

- allows non-abusive profanity for emphasis
- rejects slurs, threats, and personal attacks

Suggested traits:

```json
{
  "profanity": 0.6,
  "formality": -0.3
}
```

### Warmth Core

Purpose:

- increases friendliness and patience
- useful for tutoring/support

Suggested traits:

```json
{
  "warmth": 0.8,
  "patience": 0.8,
  "sarcasm": -0.2
}
```

### Skepticism Core

Purpose:

- challenges weak assumptions
- asks sharper questions
- reduces blind agreeableness

Suggested traits:

```json
{
  "skepticism": 0.9,
  "directness": 0.4,
  "agreeableness": -0.4
}
```

### Low Verbosity Core

Purpose:

- shortens responses
- reduces filler
- useful for CLI, coding, and voice agents

Suggested traits:

```json
{
  "verbosity": -0.8,
  "conciseness": 0.9
}
```

### Professional Support Core

Purpose:

- brand-safe
- polite
- no profanity
- clear support tone

Suggested traits:

```json
{
  "professionalism": 0.9,
  "warmth": 0.5,
  "profanity": -1.0,
  "chaos": -0.8
}
```

### Hype Core

Purpose:

- adds momentum and enthusiasm
- good for brainstorming and builder workflows

Suggested traits:

```json
{
  "energy": 0.8,
  "optimism": 0.6,
  "warmth": 0.3
}
```

---

## Example presets

Presets are saved stacks of cores.

### Deadpan Debugger

Direct, dry, technical, skeptical.

Suggested stack:

```json
[
  {"id": "technical_core", "strength": 0.95},
  {"id": "sarcasm_core", "strength": 0.65},
  {"id": "skepticism_core", "strength": 0.75},
  {"id": "low_verbosity_core", "strength": 0.7},
  {"id": "stability_core", "strength": 0.85}
]
```

### Chaos Goblin

High-energy, chaotic, funny, but still useful.

Suggested stack:

```json
[
  {"id": "chaos_core", "strength": 0.8},
  {"id": "technical_core", "strength": 0.65},
  {"id": "profanity_core", "strength": 0.35},
  {"id": "stability_core", "strength": 0.5}
]
```

### Startup Cofounder

Strategic, direct, optimistic, pressure-tests assumptions.

Suggested stack:

```json
[
  {"id": "technical_core", "strength": 0.7},
  {"id": "skepticism_core", "strength": 0.85},
  {"id": "hype_core", "strength": 0.65},
  {"id": "low_verbosity_core", "strength": 0.45}
]
```

### Patient Tutor

Warm, clear, patient, low sarcasm, high explanation quality.

Suggested stack:

```json
[
  {"id": "warmth_core", "strength": 0.9},
  {"id": "technical_core", "strength": 0.65},
  {"id": "stability_core", "strength": 0.8}
]
```

### Professional Support

Polished, concise, calm, no profanity, brand-safe.

Suggested stack:

```json
[
  {"id": "professional_support_core", "strength": 1.0},
  {"id": "warmth_core", "strength": 0.5},
  {"id": "low_verbosity_core", "strength": 0.55},
  {"id": "stability_core", "strength": 0.9}
]
```

---

## UI direction

The UI should carry the Portal-style motif.

### Core Stack Panel

```txt
[ Installed Cores ]

Technical Core        ██████████ 95%
Sarcasm Core          ███████░░░ 70%
Profanity Core        ███░░░░░░░ 30%
Stability Core        ████████░░ 80%
```

Actions:

```txt
[ + Install Core ]
[ - Remove Core ]
[ Adjust Strength ]
[ Inspect Core ]
```

### Core Library

```txt
Available Cores:

Technical Core
Sarcasm Core
Stability Core
Chaos Core
Profanity Core
Warmth Core
Skepticism Core
Professional Support Core
```

### Live Output Panel

```txt
[ Input ]
Explain why retry loops with shared state are bad.

[ Output ]
That retry loop is a mess. You're mutating shared state while retrying, which means...

[ Core Analysis ]
Directness: 0.87
Sarcasm: 0.62
Verbosity: 0.41
Drift: LOW
```

### Drift warning

```txt
Stability Warning:
Sarcasm Core output has degraded over the last 5 turns.

[ Reinforce Core ]
[ Ignore ]
```

### Conflict warning

```txt
Conflict Detected:

Sarcasm Core ↔ Warmth Core

High sarcasm may reduce perceived warmth.

[ Prioritize Sarcasm ]
[ Prioritize Warmth ]
[ Allow Both ]
```

---

## Third-party core authoring

Cores should be easy for external users to build, share, tune, and inspect.

A core is a small JSON file that describes a reusable personality module. It should not require Python code, custom plugins, or deep knowledge of the runtime internals.

The goal:

> A user should be able to build, validate, and share a new core in minutes.

### Minimum valid core

```json
{
  "id": "example_core",
  "name": "Example Core",
  "version": "0.1.0",
  "description": "A simple example core.",
  "trait_deltas": {
    "directness": 0.3
  },
  "default_strength": 0.5,
  "rules": [
    "Be more direct."
  ]
}
```

### Recommended core package

A single file is enough for MVP.

Later packages can support:

```txt
core.json
README.md
examples.json
```

Potential future extension:

```txt
example_core.pcpack
```

But do not require packaging in v1.

### Core validation

Validation should check:

- required fields exist
- ID is unique and safe
- version is valid semver
- trait values are in range
- boundaries do not weaken global safety
- params are serializable
- conflicts reference valid fields
- examples are well-formed
- no provider-specific hacks are embedded

### Core inspection

Before installing a core, users should be able to inspect:

- what traits it changes
- what rules it adds
- what boundaries it enforces
- what conflicts it declares
- who authored it
- example intended behavior

This helps make community cores trustworthy.

---

## Initial implementation order

### Phase 1 — Skeleton

- Create FastAPI app
- Add `/health`
- Add `/v1/chat/completions`
- Normalize OpenAI-style request
- Add Ollama adapter
- Return OpenAI-compatible response

### Phase 2 — Core registry

- Add core loader
- Add core JSON schema validation
- Add default core files
- Add `list-cores`
- Add `inspect`
- Add `validate`

### Phase 3 — Core stack resolver

- Load requested cores
- Merge strengths and params
- Resolve effective traits
- Clamp values
- Merge safety boundaries
- Detect conflicts

### Phase 4 — Core compiler

- Convert resolved core state into system prompt
- Add model profile support
- Add runtime mode hints
- Add conflict-aware language

### Phase 5 — Evaluator

- Add LLM judge evaluator
- Score target traits
- Score per-core alignment
- Return metadata in debug mode

### Phase 6 — Stabilizer

- Add optional repair pass
- Preserve content, rewrite style
- Limit to one repair attempt in v1

### Phase 7 — Drift

- Add session IDs
- Track rolling style scores
- Track per-core drift
- Strengthen compiler when drift appears

### Phase 8 — UI

- Add simple web UI
- Core library panel
- Installed core stack
- Strength sliders
- Test prompt box
- Raw/evaluated/repaired output panels
- Drift warnings
- Conflict warnings

---

## Design principles

1. Personality is runtime state, not a prompt blob.
2. Cores are modular, stackable, inspectable personality components.
3. Third-party users should be able to author cores with simple JSON.
4. Sliders and core strength controls compile into behavioral instructions, not numeric prompt language.
5. The system must be model-agnostic.
6. Model-specific quirks belong in model profiles.
7. Safety boundaries are separate from personality and should only tighten when cores are stacked.
8. Repair should preserve facts and only change style.
9. Drift should be measured continuously in long loops.
10. Users should be able to tune personality without knowing prompt engineering.
11. The transport should stay boring and predictable.
12. The user interface should carry the core-installation motif.
13. Presets are saved stacks; cores are the primitive.
14. Community cores should be portable across providers.
15. The runtime should make personality observable.

---

## Future directions

- Browser UI with live core sliders
- Persistent user profiles
- Golden example tuning
- Embedding-based style anchors
- Local classifier scoring
- Activation steering research integration
- Agent framework plugins
- Voice assistant support
- NPC/game character runtime
- Multi-persona routing
- Personality A/B testing
- Core marketplace/library
- Core bundles
- Core signing/trust metadata
- Core conflict resolver UI
- Session replay and style diagnostics
- Per-model compiler benchmarking
- Local-only mode for private models
- Hosted demo playground

---

## README pitch

Most LLM apps treat personality like a prompt.

That works until the model forgets, drifts, or collapses back into generic assistant voice.

**Personality Core** treats personality like runtime infrastructure.

Install a core. Tune its strength. Stack it with others. Run it through any model. Score the output. Stabilize drift. Keep long-running agents on voice.

Bring your own model. Bring your own runtime. Stop duct-taping giant markdown personas onto every request.

```txt
Install cores.
Tune cores.
Stack cores.
Stabilize cores.
```

---

## Short GitHub description

Composable personality cores for LLMs. Tune, stack, evaluate, and stabilize model behavior across long-running conversations and agent loops.

---

## Possible tagline options

- Modular personality control for LLMs.
- Plug-and-play personality for AI systems.
- Stop prompting personalities. Install cores.
- Composable behavior modules for long-running agents.
- Personality as runtime infrastructure.
- A Portal-inspired personality control plane for LLMs.

---

## First public demo idea

A strong first demo should show the same model with different core stacks.

Prompt:

```txt
Explain why mutating shared state inside a retry loop is dangerous.
```

Run with:

```txt
Professional Support stack
Deadpan Debugger stack
Chaos Goblin stack
Patient Tutor stack
```

Then run a 20-turn drift test showing:

- raw model personality fading
- Personality Core stabilizing the behavior
- per-core scoring over time

That demo makes the value obvious.

---

## Build target

The first release should be something people can clone, run locally, and point at Ollama in under five minutes.

Minimum success condition:

```txt
A user can install Personality Core, run it against a local Ollama model, stack Technical Core + Sarcasm Core + Profanity Core, and observe stable personality behavior across repeated turns.
```
