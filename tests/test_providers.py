from fastapi.testclient import TestClient

from personality_core.app import api
from personality_core.adapters.openai import split_provider_model


def test_provider_catalog_lists_supported_routes():
    client = TestClient(api)

    response = client.get("/v1/providers")

    assert response.status_code == 200
    data = response.json()
    provider_ids = {provider["id"] for provider in data["providers"]}
    assert {"ollama", "openai", "openrouter", "lmstudio"} <= provider_ids


def test_openai_compatible_model_prefix_split():
    assert split_provider_model("openai/gpt-4.1-mini", "openai") == ("openai", "gpt-4.1-mini")
    assert split_provider_model("openrouter/openai/gpt-4o-mini", "openai") == ("openrouter", "openai/gpt-4o-mini")
    assert split_provider_model("gpt-4.1-mini", "openai") == ("openai", "gpt-4.1-mini")
