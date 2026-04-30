# Runtime Mutations

Runtime mutations let a core do more than suggest behavior in a prompt. A mutation is a backend behavior transform that resolves with the stack and is applied after the model call.

This is useful for narrow, configurable behavior modules:

- enforce house terminology
- add lightweight dialect or voice markers
- normalize labels before downstream tools read output
- simulate noisy user behavior in test agents

## Mutation Shape

```json
{
  "type": "replace_terms",
  "rate": 1.0,
  "whole_words": true,
  "preserve_case": true,
  "terms": {
    "customer": "member",
    "issue": "case"
  }
}
```

The effective rate is:

```text
mutation.rate * core strength
```

At strength `1.0`, every matching whole word is replaced. At lower strengths, replacements are applied deterministically to a subset of occurrences so behavior is repeatable.

## Example Core Shape

Core Creator can draft this kind of shape when the user describes concrete lexical behavior, such as house vocabulary or style markers.

```json
{
  "id": "terminology_core",
  "name": "Terminology Core",
  "kind": "style",
  "default_strength": 0.8,
  "mutations": [
    {
      "type": "replace_terms",
      "rate": 1.0,
      "whole_words": true,
      "preserve_case": true,
      "terms": {
        "customer": "member",
        "issue": "case"
      }
    }
  ]
}
```

## Pipeline Position

```text
model output -> runtime mutations -> contract evaluation -> optional repair -> runtime mutations -> final output
```

Mutations are also compiled into the system prompt as preferences. This gives the model a chance to produce the behavior naturally while still allowing the runtime to enforce concrete transforms.

## Current Limitations

Only `replace_terms` is implemented. The schema is intentionally open so future mutation types can cover typo simulation, casing transforms, glossary enforcement, redaction, and other chain-safe behavior plugins.
