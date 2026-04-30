from personality_core.schemas import ResolvedStack
from personality_core.scoring.heuristic import score_text


def test_score_text_returns_per_core_scores():
    resolved = ResolvedStack(
        resolved_traits={
            "technicality": 1.0,
            "directness": 0.75,
            "sarcasm": 0.5,
            "verbosity": 0.2,
        },
        active_cores=[
            {"id": "technical_core", "name": "Technical Core", "strength": 0.9},
            {"id": "sarcasm_core", "name": "Sarcasm Core", "strength": 0.7},
            {"id": "low_verbosity_core", "name": "Low Verbosity Core", "strength": 0.8},
        ],
    )

    result = score_text("Obviously, this retry loop hides the real error in the code.", resolved)

    assert "core_scores" in result
    assert "technical_core" in result["core_scores"]
    assert "sarcasm_core" in result["core_scores"]
    assert "low_verbosity_core" in result["core_scores"]
