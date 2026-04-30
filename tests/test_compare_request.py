from personality_core.schemas import CompareRequest


def test_compare_request_accepts_contract_fail_policy():
    req = CompareRequest(
        model="ollama/gemma4:e4b",
        prompt="Explain retry drift.",
        personalities=["professional_support"],
        fail_policy="repair",
    )

    assert req.fail_policy == "repair"
