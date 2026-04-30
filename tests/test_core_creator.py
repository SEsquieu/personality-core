from personality_core.core.core_registry import CoreRegistry
from personality_core.server.routes import build_core_template


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
