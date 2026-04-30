# Personality Core Demo Kit

The demo kit is the fastest way to show why Personality Core is more than a prompt preset folder.

It runs the same prompt through multiple saved personality presets, then prints the active cores, heuristic scores, issues, warnings, and model output for each one.

## Compare Presets

```bash
personality-core compare "Explain why retries hide real errors." \
  --model "ollama/gemma4:e4b" \
  --max-tokens 260
```

Default presets:

- `professional_support`
- `deadpan_debugger`
- `patient_tutor`
- `startup_cofounder`
- `chaos_goblin`

## Named Demo Prompts

Use `--demo` when you want repeatable comparisons without retyping prompts:

```bash
personality-core compare --demo retry_loop
personality-core compare --demo angry_customer
personality-core compare --demo code_review
personality-core compare --demo startup_pitch
personality-core compare --demo debugging
```

## Output Modes

Show only diagnostics:

```bash
personality-core compare --demo retry_loop --summary
```

Print machine-readable JSON:

```bash
personality-core compare --demo code_review --json
```

Save a run:

```bash
personality-core compare --demo angry_customer --save runs/angry-customer.json
```

Saved output includes:

- model
- prompt
- demo id
- personality id
- generated content
- active cores
- aggregate `core_match`
- per-core `core_scores`
- evaluator issues
- backend warnings
- model `done_reason`

## Evaluator Notes

The evaluator is intentionally heuristic in this MVP. `core_scores` are useful for directionally spotting under-expressed cores, not for final quality judgment.

The next major evaluator step is golden-example scoring, where cores and personality presets can include style anchors that model output is compared against.
