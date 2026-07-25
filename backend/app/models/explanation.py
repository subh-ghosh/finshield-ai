"""Explanation model representing natural language reasoning behind threats."""

from dataclasses import dataclass

@dataclass
class Explanation:
    """Consolidates summary descriptions and component evidence statements for LLM/planner parsing."""
    summary: str
    rule_evidence: str
    ml_evidence: str
    behavioral_evidence: str
