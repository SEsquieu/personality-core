# Core Stack Workflow

The main product workflow is the Core Stack, not the comparison demo.

A stack is the active set of installed personality cores for a model call:

```json
[
  {"id": "technical_core", "strength": 0.95},
  {"id": "sarcasm_core", "strength": 0.65},
  {"id": "low_verbosity_core", "strength": 0.75}
]
```

## Runtime Loop

```text
install cores -> tune strengths -> resolve stack -> compile stack -> run model -> evaluate output
```

## Short-Circuit Modes

Use these when integrating Personality Core into an existing chain without spending model tokens.

Resolve:

```http
POST /v1/stack/resolve
```

Returns resolved traits, active cores, boundaries, conflicts, and core trace.

Compile:

```http
POST /v1/stack/compile
```

Returns everything from resolve plus the compiled system prompt.

Run:

```http
POST /v1/stack/run
```

Calls the model with the active stack and returns output, warnings, evaluation, and debug data.

## Frontend

The workbench defaults to Stack Editor mode:

- load a preset into the active stack
- add/remove cores
- tune strength sliders
- resolve without model calls
- compile without model calls
- run the active stack
- inspect resolved traits and core trace

Compare mode remains useful for demos, but Stack Editor is the in-chain workflow.
