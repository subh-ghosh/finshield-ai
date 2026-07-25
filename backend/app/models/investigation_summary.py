"""Investigator summary containing natural language explanations and action steps."""

from dataclasses import dataclass

@dataclass
class InvestigationSummary:
    """Consolidates text narratives and interpretation statements for investigator review."""
    narrative: str
    score_interpretation: str
    conclusion: str
