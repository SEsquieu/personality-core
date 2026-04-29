import requests

payload = {
    "model": "ollama/gemma4:e4b",
    "messages": [{"role": "user", "content": "Explain why the build failed because config is inconsistent and logs are unclear."}],
    "cores": [
        {"id": "technical_core", "strength": 0.9},
        {"id": "sarcasm_core", "strength": 0.7},
        {"id": "profanity_core", "strength": 0.5},
    ],
    "debug": True,
}

r = requests.post("http://127.0.0.1:8787/v1/chat/completions", json=payload, timeout=120)
r.raise_for_status()
print(r.json()["choices"][0]["message"]["content"])
