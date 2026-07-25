"""Model definition for structured rule check evaluations."""

from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class RuleEvaluation:
    """Represents the results of evaluating a single customer record against an AML rule.

    Carries structured evidence and flag states for downstream scoring.
    """
    triggered: bool
    rule_id: str
    rule_name: str
    score: int
    severity: str
    explanation: str
    evidence: Dict[str, Any]
