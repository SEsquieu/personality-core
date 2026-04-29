# Curl Ollama example

```bash
curl http://127.0.0.1:8787/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/gemma4:e4b",
    "messages": [{"role": "user", "content": "Explain why retry loops with shared state are dangerous."}],
    "cores": [
      {"id": "technical_core", "strength": 0.95},
      {"id": "sarcasm_core", "strength": 0.7},
      {"id": "profanity_core", "strength": 0.35}
    ],
    "stabilizer": {"enabled": true},
    "debug": true
  }'
```
