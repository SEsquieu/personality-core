# Behavior Contracts

Personality Core can enforce runtime behavior contracts, not just personality traits. Personality is one behavior category; format, workflow, safety, reasoning, and domain constraints can live in the same stack.

## Why It Matters

Agent chains fail when model output drifts away from the contract the next step expects:

- prose instead of JSON
- missing required fields
- tone drift in customer workflows
- unsupported certainty
- verbose output where a tool expects a short value

Behavior contracts let a core declare what must be true about the output. The runtime compiles the contract into the prompt, evaluates the response, and applies the selected fail policy. This makes the layer useful in the middle of an agent chain where downstream steps need predictable output.

## Core Kinds

Cores now have a `kind` field:

```json
{
  "id": "structured_json_output_core",
  "name": "Structured JSON Output Core",
  "kind": "format"
}
```

Suggested kinds:

- `personality`
- `format`
- `safety`
- `reasoning`
- `workflow`
- `domain`

## JSON Output Contract

`structured_json_output_core` ships as the first contract core. It requires a valid JSON object with:

```json
{
  "answer": "string",
  "confidence": 0.86,
  "notes": ["array of short strings"]
}
```

The core declares this with a contract:

```json
{
  "type": "json_object",
  "required_fields": ["answer", "confidence", "notes"],
  "schema": {
    "type": "object",
    "required": ["answer", "confidence", "notes"],
    "properties": {
      "answer": { "type": "string" },
      "confidence": { "type": "number" },
      "notes": { "type": "array" }
    }
  }
}
```

## Fail Policies

Runtime requests can choose a contract fail policy:

- `warn`: return output and include contract warnings
- `repair`: ask the model to repair format/contract drift
- `block`: return no content when the contract fails
- `raw`: return the raw model output without intervention

The workbench defaults to `repair`.

API example:

```json
{
  "model": "ollama/gemma4:e4b",
  "messages": [{ "role": "user", "content": "Summarize why retries hide errors." }],
  "cores": [
    { "id": "structured_json_output_core", "strength": 1.0 },
    { "id": "technical_core", "strength": 0.8 }
  ],
  "fail_policy": "repair",
  "debug": true
}
```

Debug output includes:

- `debug.contract_evaluation`
- `debug.fail_policy`
- normal style evaluation
- resolved stack and active contracts

## Team Workflow

```text
create contract core -> add to stack -> run model -> evaluate contract -> warn/repair/block/raw
```

This lets teams pin behavior at the middleware layer instead of scattering fragile prompt text across every agent node.
