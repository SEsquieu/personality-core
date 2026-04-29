import requests

history = []
for turn in range(1, 6):
    history.append({"role": "user", "content": f"Turn {turn}: Explain another reason shared mutable state in retry loops is dangerous."})
    payload = {
        "model": "ollama/gemma4:e4b",
        "messages": history,
        "cores": [
            {"id": "technical_core", "strength": 0.95},
            {"id": "sarcasm_core", "strength": 0.7},
            {"id": "low_verbosity_core", "strength": 0.7},
            {"id": "stability_core", "strength": 0.85},
        ],
        "stabilizer": {"enabled": True, "threshold": 0.78},
        "debug": True,
    }
    r = requests.post("http://127.0.0.1:8787/v1/chat/completions", json=payload, timeout=120)
    r.raise_for_status()
    msg = r.json()["choices"][0]["message"]
    print("\n--- turn", turn, "---")
    print(msg["content"])
    history.append({"role": "assistant", "content": msg["content"]})
