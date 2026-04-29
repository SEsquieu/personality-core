from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8787/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="ollama/gemma4:e4b",
    messages=[{"role": "user", "content": "Explain why config drift is annoying."}],
    extra_body={
        "cores": [
            {"id": "technical_core", "strength": 0.9},
            {"id": "sarcasm_core", "strength": 0.7},
            {"id": "low_verbosity_core", "strength": 0.7},
        ],
        "stabilizer": {"enabled": True},
    },
)
print(response.choices[0].message.content)
