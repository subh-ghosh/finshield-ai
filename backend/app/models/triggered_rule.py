"""Model definition for successfully triggered AML rules."""

from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class TriggeredRule:
    """Represents a rule violation triggered by a customer.

    Stores human-readable reasons, contributing score, and structured evidence.
    """
    rule_id: str
    rule_name: str
    score: int
    severity: str
    description: str
    explanation: str
    evidence: Dict[str, Any]
