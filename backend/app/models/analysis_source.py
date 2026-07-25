"""Enum defining the valid source tags for risk and anomaly evaluation engines."""

from enum import Enum

class AnalysisSource(str, Enum):
    """Enumeration of standard sources generating transaction analysis results.

    Inherits from (str, Enum) to ensure direct string comparison and JSON serialization
    compatibility across downstream components.
    """
    RULE_ENGINE = "rule_engine"
    ISOLATION_FOREST = "isolation_forest"
    HYBRID_RISK = "hybrid_risk"
    GRAPH_ANALYSIS = "graph_analysis"
    LLM = "llm"

    def __str__(self) -> str:
        return self.value
