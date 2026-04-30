from __future__ import annotations
from personality_core.schemas import ResolvedStack

class Stabilizer:
    def build_repair_messages(self, original_messages: list[dict], raw_output: str, resolved: ResolvedStack, evaluation: dict) -> list[dict]:
        traits = resolved.resolved_traits
        instruction = f"""Rewrite the assistant response to better match the active Personality Core stack.
Preserve all technical claims and recommendations.
Do not add new facts.
Do not weaken safety boundaries.
Target traits: {traits}
Active cores: {[c['id'] for c in resolved.active_cores]}
Evaluation issues: {evaluation.get('issues', [])}
Original assistant response:\n{raw_output}
"""
        return [
            {"role": "system", "content": "You are the Personality Core Stabilizer. Rewrite style only. Preserve meaning."},
            {"role": "user", "content": instruction},
        ]

    def build_contract_repair_messages(self, original_messages: list[dict], raw_output: str, resolved: ResolvedStack, contract_evaluation: dict) -> list[dict]:
        instruction = f"""Repair the assistant response so it satisfies the active Personality Core output contracts.
Do not add unsupported facts.
Preserve the user's requested content.
Return only the repaired final answer.

Contracts: {resolved.contracts}
Contract issues: {contract_evaluation.get('issues', [])}
Original messages: {original_messages}
Original assistant response:\n{raw_output}
"""
        return [
            {"role": "system", "content": "You are the Personality Core Contract Stabilizer. Repair format and contract drift only."},
            {"role": "user", "content": instruction},
        ]
