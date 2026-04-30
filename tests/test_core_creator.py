from personality_core.core.core_registry import CoreRegistry
from personality_core.core.pipeline import PersonalityPipeline
from personality_core.schemas import CoreDraftRequest
from personality_core.server.routes import build_core_template, normalize_model_core_data


def test_registry_validates_creator_core_payload():
    registry = CoreRegistry("cores")
    core = {
        "id": "concise_review_core",
        "name": "Concise Review Core",
        "version": "0.1.0",
        "description": "Keeps review feedback concise and actionable.",
        "author": "test",
        "trait_deltas": {"directness": 0.4, "verbosity": -0.3},
        "default_strength": 0.7,
        "params": {},
        "rules": ["Lead with the most important risk."],
        "boundaries": {"preserve_task_accuracy": True},
        "evaluation_weights": {"clarity": 0.8},
        "conflicts_with": [],
        "examples": [],
    }

    validated = registry.validate_definition(core, source="test")

    assert validated.id == "concise_review_core"
    assert validated.default_strength == 0.7


def test_core_template_is_schema_valid():
    template = build_core_template()

    assert template.id == "custom_example_core"
    assert template.rules
    assert template.boundaries["preserve_task_accuracy"] is True


def test_bare_local_model_names_route_to_ollama():
    pipeline = PersonalityPipeline("cores", "personalities", "model_profiles")

    assert pipeline.adapter_for("gemma4:e4b") is pipeline.ollama
    assert pipeline.adapter_for("ollama/gemma4:e4b") is pipeline.ollama


def test_model_core_draft_normalizes_common_llm_json_variants():
    registry = CoreRegistry("cores")
    req = CoreDraftRequest(intent="A duplicitous uncertainty core.", name="Liar Core")
    data = normalize_model_core_data(
        {
            "id": "Liar Core",
            "name": "Liar Core",
            "trait_deltas": {"skepticism": 1.5, "warmth": "-0.2"},
            "default_strength": 2,
            "rules": ["Add uncertainty."],
            "boundaries": {},
            "conflicts_with": ["TruthCore"],
        },
        req,
        "Liar Core",
        req.intent,
    )

    validated = registry.validate_definition(data, source="test")

    assert validated.id == "liar_core"
    assert validated.trait_deltas["skepticism"] == 1.0
    assert validated.default_strength == 1.0
    assert validated.conflicts_with == [{"core": "TruthCore", "reason": "Model-reported conflict."}]
