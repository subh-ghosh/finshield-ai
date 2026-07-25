"""Behavioral risk analyzer implementation using config-driven indicators mapping."""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from app.config import ml_config
from app.ml.interfaces.behavioral_risk_analyzer import IBehavioralRiskAnalyzer
from app.models.risk_factor import RiskFactor

class BehavioralRiskAnalyzer(IBehavioralRiskAnalyzer):
    """Evaluates customer behavioral features using configured indicator weights and scales."""

    def __init__(self, indicators_config: Dict[str, Dict[str, float]] = None):
        """Initializes the analyzer with the given configuration dictionary.

        Args:
            indicators_config: Optional indicators overrides.
        """
        self.config = indicators_config if indicators_config is not None else getattr(
            ml_config, "BEHAVIORAL_INDICATORS", {}
        )

    def analyze(self, customer_row: pd.Series) -> Tuple[float, Dict[str, float], List[RiskFactor]]:
        """Analyzes customer metrics against indicators configuration.

        Args:
            customer_row: Customer behavioral features Series.

        Returns:
            Tuple[float, Dict[str, float], List[RiskFactor]]: 
                - Fused behavioral score (0.0 to 1.0)
                - Dictionary mapping indicator name to normalized score
                - List of generated RiskFactor objects
        """
        breakdown: Dict[str, float] = {}
        risk_factors: List[RiskFactor] = []
        
        weighted_score_sum = 0.0
        total_weight_sum = 0.0

        for col, settings in self.config.items():
            max_val = settings.get("max", 1.0)
            weight = settings.get("weight", 0.0)
            
            # Fetch raw value defensively
            raw_value = float(customer_row.get(col, 0.0))
            if pd.isna(raw_value) or np.isinf(raw_value):
                raw_value = 0.0
                
            # Normalize and clip to [0.0, 1.0]
            normalized = np.clip(raw_value / max_val if max_val > 0 else 0.0, 0.0, 1.0)
            breakdown[col] = normalized
            
            weighted_score_sum += normalized * weight
            total_weight_sum += weight

            # Expose as a RiskFactor if the indicator has a meaningful contribution
            if normalized > 0.1:
                severity = self._classify_severity(normalized)
                risk_factors.append(
                    RiskFactor(
                        name=f"BEHAVIORAL_{col.upper()}",
                        score=normalized,
                        severity=severity,
                        description=f"Behavioral indicator {col} is elevated at {raw_value:.2f} (normalized: {normalized:.2f})",
                        source="BEHAVIORAL"
                    )
                )

        # Normalize score sum by weight sum to handle customized config changes safely
        final_score = (weighted_score_sum / total_weight_sum) if total_weight_sum > 0 else 0.0
        
        return final_score, breakdown, risk_factors

    @staticmethod
    def _classify_severity(score: float) -> str:
        """Classifies severity brackets based on score."""
        if score >= 0.75:
            return "CRITICAL"
        if score >= 0.50:
            return "HIGH"
        if score >= 0.25:
            return "MEDIUM"
        return "LOW"
