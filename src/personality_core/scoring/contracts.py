from __future__ import annotations
import json
import re
from typing import Any
from personality_core.schemas import ResolvedStack


def evaluate_contracts(text: str, resolved: ResolvedStack) -> dict[str, Any]:
    results = [evaluate_contract(text, contract) for contract in resolved.contracts]
    failed = [result for result in results if not result["ok"]]
    return {
        "ok": not failed,
        "repair_needed": bool(failed),
        "results": results,
        "issues": [issue for result in failed for issue in result["issues"]],
    }


def evaluate_contract(text: str, contract: dict[str, Any]) -> dict[str, Any]:
    contract_type = contract.get("type")
    if contract_type == "json_object":
        return evaluate_json_object(text, contract)
    return {"type": contract_type or "unknown", "core_id": contract.get("core_id"), "ok": True, "issues": []}


def evaluate_json_object(text: str, contract: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    parsed = extract_json_object(text)
    if parsed is None:
        issues.append("Output contract failed: response is not a valid JSON object.")
        return {"type": "json_object", "core_id": contract.get("core_id"), "ok": False, "issues": issues}
    required = [str(field) for field in contract.get("required_fields", [])]
    missing = [field for field in required if field not in parsed]
    if missing:
        issues.append("Output contract failed: missing required JSON fields: " + ", ".join(missing) + ".")
    schema = contract.get("schema")
    if isinstance(schema, dict):
        issues.extend(validate_schema_subset(parsed, schema))
    return {"type": "json_object", "core_id": contract.get("core_id"), "ok": not issues, "issues": issues}


def extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            parsed = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None


def validate_schema_subset(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = schema.get("required", [])
    if isinstance(required, list):
        missing = [str(field) for field in required if str(field) not in data]
        if missing:
            issues.append("Output contract failed: missing schema fields: " + ", ".join(missing) + ".")
    properties = schema.get("properties", {})
    if isinstance(properties, dict):
        for field, spec in properties.items():
            if field not in data or not isinstance(spec, dict):
                continue
            expected = spec.get("type")
            if expected and not type_matches(data[field], str(expected)):
                issues.append(f"Output contract failed: field {field} should be {expected}.")
    return issues


def type_matches(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, int | float) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return True
