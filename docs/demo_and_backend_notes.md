# Demo and Backend Notes

This project should be easy to try without forcing a single local model setup.

## Demo Defaults

`personality-core demo` prints starter `personality-core chat` commands. The demo does not call a model by itself; it only shows commands a user can run.

The generated commands include:

- an explicit `--model`
- an explicit `--max-tokens 300`
- `--debug` so users can inspect the resolved core stack

The demo intentionally leaves `--stabilizer` off. The stabilizer can trigger a second model call, so users should try it after the fast path works.

Personality Core sends `think: false` to Ollama by default. This keeps the first-run demo focused on visible assistant output instead of spending the token budget on a hidden reasoning trace.

## Model Selection

The default model is controlled by `PERSONALITY_CORE_DEFAULT_MODEL`.

If unset, the default is:

```bash
ollama/gemma4:e4b
```

Users can override the model per command:

```bash
personality-core demo --model "ollama/llama3.2:3b"
personality-core chat "Why is config drift painful?" --model "ollama/llama3.2:3b"
```

## Ollama Behavior

Models with the `ollama/` prefix route through the Ollama adapter.

Relevant environment variables:

```bash
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT=300
```

If Ollama is unavailable or too slow, the CLI now prints a short backend error instead of a raw `httpx` traceback.

If Ollama returns an empty assistant message, Personality Core treats that as a backend error. A normal `chat` run should print the assistant response first, then print `Core debug` when `--debug` is enabled.

If the response is empty:

- confirm the model is a chat-capable Ollama model
- leave thinking disabled, or pass `--think` only after the fast path works
- try a larger `--max-tokens` value if `done='length'`
- run the command again after the model finishes loading
- try a smaller local model for the first demo

If the response starts correctly but cuts off mid-sentence or mid-list, check `debug.model_response.done_reason`. A value of `length` means Ollama hit `num_predict`; increase `--max-tokens`.

## First-Run Guidance

For a quick check, prefer a small local model and a short output cap:

```bash
personality-core chat "Explain why retries can hide real errors." \
  --model "ollama/llama3.2:3b" \
  --cores "technical_core:0.9,sarcasm_core:0.5,low_verbosity_core:0.8" \
  --max-tokens 180 \
  --debug
```

Once that works, add `--stabilizer` to test drift repair.

## Personality Comparison

`personality-core compare` runs one prompt through several saved personality presets:

```bash
personality-core compare "Explain why retries hide real errors." \
  --model "ollama/llama3.2:3b" \
  --max-tokens 260
```

Default presets:

- `professional_support`
- `deadpan_debugger`
- `patient_tutor`
- `startup_cofounder`
- `chaos_goblin`

Each result prints:

- active cores
- heuristic `core_match`
- detected mode
- backend `done_reason`
- evaluator issues
- truncation/backend warnings
- generated response

This command is meant to be the terminal demo for the project: same prompt, same model, different installed core stack.
