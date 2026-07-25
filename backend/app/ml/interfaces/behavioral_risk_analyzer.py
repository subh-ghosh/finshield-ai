"""Behavioral risk analyzer abstract interface contract definition."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Tuple
from app.models.risk_factor import RiskFactor

class IBehavioralRiskAnalyzer(ABC):
    """Interface defining the capability to inspect customer properties and return scores + evidence."""

    @abstractmethod
    def analyze(self, customer_row: pd.Series) -> Tuple[float, Dict[str, float], list[RiskFactor]]:
        """Evaluates customer behavioral traits against rules indicators configuration.

        Args:
            customer_row: Single customer record Series.

        Returns:
            Tuple[float, Dict[str, float], list[RiskFactor]]: 
                - Behavioral Score (0.0 to 1.0)
                - Breakdown of normalized sub-scores
                - List of generated RiskFactor evidence objects
        """
        pass
