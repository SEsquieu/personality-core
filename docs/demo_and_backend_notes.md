# Demo and Backend Notes

This project should be easy to try without forcing a single local model setup.

## Demo Defaults

`personality-core demo` prints starter `personality-core chat` commands. The demo does not call a model by itself; it only shows commands a user can run.

The generated commands include:

- an explicit `--model`
- an explicit `--max-tokens 220`
- `--debug` so users can inspect the resolved core stack

The demo intentionally leaves `--stabilizer` off. The stabilizer can trigger a second model call, so users should try it after the fast path works.

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

## First-Run Guidance

For a quick check, prefer a small local model and a short output cap:

```bash
personality-core chat "Explain why retries can hide real errors." \
  --model "ollama/llama3.2:3b" \
  --cores "technical_core:0.9,sarcasm_core:0.5,low_verbosity_core:0.8" \
  --max-tokens 120 \
  --debug
```

Once that works, add `--stabilizer` to test drift repair.
