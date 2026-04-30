# Core Creator

Core Creator turns a plain-language behavior intent into a schema-valid Personality Core JSON file.

The creator now supports both hand-authored JSON and model-assisted drafting. The UI starts with a valid template, and `Draft` sends the intent to the currently selected model endpoint before the result is validated.

## Workflow

```text
load template or describe intent -> draft JSON -> edit JSON -> validate -> install -> add to stack
```

## Frontend

Open the workbench:

```bash
npm run dev
```

Use the `Core Creator` mode:

- enter a core name
- describe the desired behavior
- click `Template` for a hand-editable scaffold, or `Draft` to ask the selected model to write one
- review or edit the JSON
- click `Validate`
- click `Install`

Installed cores are written to `cores/{core_id}.json`, the registry reloads, and the new core is added to the active stack.

## API

Template:

```http
GET /v1/cores/template
```

Draft:

```http
POST /v1/cores/draft
```

`POST /v1/cores/draft` accepts:

```json
{
  "intent": "A concise reviewer that leads with risks and concrete fixes.",
  "name": "Concise Review Core",
  "author": "local",
  "model": "ollama/gemma4:e4b",
  "max_tokens": 900,
  "temperature": 0.2,
  "think": false
}
```

When `model` is present, the backend calls that model adapter and asks for strict core JSON. When `model` is omitted, the backend uses the deterministic draft path.

Validate:

```http
POST /v1/cores/validate
```

Install:

```http
POST /v1/cores/install
```

Install rejects duplicate core IDs unless `overwrite` is true.

## Core Format Framework

Every core is a JSON object with this shape:

```json
{
  "id": "custom_example_core",
  "name": "Custom Example Core",
  "version": "0.1.0",
  "description": "A starting point for a hand-authored personality core.",
  "author": "local",
  "trait_deltas": {
    "directness": 0.25,
    "warmth": 0.15,
    "verbosity": -0.2,
    "technicality": 0.2
  },
  "default_strength": 0.65,
  "params": {},
  "rules": [
    "Preserve task accuracy over style.",
    "Keep the behavior visible without overwhelming the user.",
    "Prefer concrete, inspectable responses."
  ],
  "boundaries": {
    "preserve_task_accuracy": true,
    "no_fake_certainty": true,
    "no_personal_attacks": true,
    "no_slurs": true
  },
  "evaluation_weights": {
    "clarity": 0.8,
    "directness": 0.6,
    "technicality": 0.4
  },
  "conflicts_with": [],
  "examples": [
    {
      "input": "Explain a risky implementation choice.",
      "ideal_style": "Lead with the risk, explain the mechanism, then give a concrete fix."
    }
  ]
}
```

Field guide:

- `id`: lowercase snake_case identifier, ending in `_core`
- `trait_deltas`: numeric pushes from `-1.0` to `1.0`
- `default_strength`: default stack strength from `0.0` to `1.0`
- `rules`: visible behavior instructions the compiler can preserve
- `boundaries`: hard limits that should survive personality styling
- `evaluation_weights`: scoring hints for drift checks
- `examples`: style anchors for humans today, and richer evaluators later

## Safety

The registry validates:

- ID format
- trait delta range
- default strength range
- required schema fields

Generated drafts and templates include conservative boundaries:

- `preserve_task_accuracy`
- `no_personal_attacks`
- `no_slurs`

Model-assisted drafts still pass through the same validation and install endpoints. Invalid model JSON never gets installed directly.
