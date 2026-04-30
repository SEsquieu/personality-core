from personality_core.scoring.contracts import evaluate_contracts
from personality_core.schemas import ResolvedStack


def json_contract_stack():
    return ResolvedStack(
        contracts=[
            {
                "type": "json_object",
                "core_id": "structured_json_output_core",
                "required_fields": ["answer", "confidence", "notes"],
                "schema": {
                    "required": ["answer", "confidence", "notes"],
                    "properties": {
                        "answer": {"type": "string"},
                        "confidence": {"type": "number"},
                        "notes": {"type": "array"},
                    },
                },
            }
        ]
    )


def test_json_contract_accepts_valid_object():
    result = evaluate_contracts('{"answer":"ok","confidence":0.9,"notes":["valid"]}', json_contract_stack())

    assert result["ok"] is True
    assert result["repair_needed"] is False


def test_json_contract_rejects_prose_output():
    result = evaluate_contracts("Here is the answer: retries hide errors.", json_contract_stack())

    assert result["ok"] is False
    assert result["repair_needed"] is True
    assert "valid JSON object" in result["issues"][0]


def test_json_contract_rejects_missing_fields():
    result = evaluate_contracts('{"answer":"ok"}', json_contract_stack())

    assert result["ok"] is False
    assert any("missing" in issue for issue in result["issues"])
