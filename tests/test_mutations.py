from personality_core.core.mutations import apply_mutations
from personality_core.schemas import ResolvedStack


def test_replace_terms_mutation_rewrites_whole_words():
    resolved = ResolvedStack(
        mutations=[
            {
                "type": "replace_terms",
                "rate": 1.0,
                "strength": 1.0,
                "whole_words": True,
                "preserve_case": True,
                "terms": {"customer": "member", "customers": "members", "issue": "case"},
                "core_id": "terminology_core",
            }
        ]
    )

    text, report = apply_mutations("Customer issue. Customers matter.", resolved)

    assert text == "Member case. Members matter."
    assert report["changed"] is True
    assert report["applied"][0]["count"] == 3


def test_mutation_strength_controls_application_rate():
    resolved = ResolvedStack(
        mutations=[
            {
                "type": "replace_terms",
                "rate": 1.0,
                "strength": 0.5,
                "terms": {"customer": "member"},
                "core_id": "terminology_core",
            }
        ]
    )

    text, report = apply_mutations("customer customer customer customer", resolved)

    assert text == "customer member customer member"
    assert report["applied"][0]["count"] == 2
