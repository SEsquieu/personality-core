# Provider Setup

Personality Core routes model calls by model prefix. The workbench uses the same selected model for stack runs, comparisons, and model-assisted core drafting.

## Quick Start

```bash
cp .env.example .env
personality-core serve --host 127.0.0.1 --port 8787
npm run dev
```

Open the workbench and use `Runtime -> Test Provider` before running a stack.

## Model Prefixes

```text
ollama/gemma4:e4b                  -> Ollama
gemma4:e4b                         -> Ollama shorthand
openai/gpt-4.1-mini                -> OpenAI-compatible chat completions
openrouter/openai/gpt-4o-mini      -> OpenRouter
lmstudio/local-model               -> LM Studio OpenAI-compatible server
```

## Ollama

```env
PERSONALITY_CORE_DEFAULT_MODEL=ollama/gemma4:e4b
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_TIMEOUT=300
```

Bare local model names also route to Ollama:

```bash
personality-core chat "Explain config drift." --model "gemma4:e4b"
```

## OpenAI

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT=300
PERSONALITY_CORE_DEFAULT_MODEL=openai/gpt-4.1-mini
```

Use models as:

```text
openai/gpt-4.1-mini
openai/gpt-4o-mini
```

## OpenRouter

```env
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_SITE_URL=
OPENROUTER_APP_NAME=Personality Core
PERSONALITY_CORE_DEFAULT_MODEL=openrouter/openai/gpt-4o-mini
```

Use models as:

```text
openrouter/openai/gpt-4o-mini
openrouter/meta-llama/llama-3.1-8b-instruct
```

## LM Studio

Start the LM Studio local server, then set:

```env
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
PERSONALITY_CORE_DEFAULT_MODEL=lmstudio/local-model
```

## Health Check API

```http
GET /v1/providers
POST /v1/providers/health
```

Example:

```json
{
  "model": "ollama/gemma4:e4b",
  "prompt": "Reply with OK.",
  "max_tokens": 24
}
```
