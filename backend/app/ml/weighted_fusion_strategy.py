"""Weighted fusion strategy combining risk scores using configurable config weights."""

from typing import Dict, Optional
from app.config import ml_config
from app.ml.interfaces.fusion_strategy import IFusionStrategy

class WeightedFusionStrategy(IFusionStrategy):
    """Combines Rule Engine, ML Outlier, and Behavioral risk scores via weighted average."""

    def __init__(self, weights: Dict[str, float] = None):
        """Initializes WeightedFusionStrategy with weights.

        Args:
            weights: Optional weights dictionary to override config settings.
        """
        self.weights = weights if weights is not None else getattr(
            ml_config, "HYBRID_WEIGHTS", {"rule_engine": 0.6, "isolation_forest": 0.3, "behavioural": 0.1}
        )
        
        # Validate weights configuration defensively
        self._validate_weights()

    def fuse(self, rule_score: float, ml_score: float, behavioral_score: float, gnn_score: Optional[float] = None) -> float:
        """Fuses multiple threat scores.

        Args:
            rule_score: Normalized Rule Engine score.
            ml_score: Isolation Forest anomaly score.
            behavioral_score: Fused behavioral analyzer score.
            gnn_score: Optional GNN per-node risk score (0-100). When provided,
                       uses V2 fusion formula: 0.3*rule + 0.3*IF + 0.4*GNN
                       as specified in the V2 implementation guide.

        Returns:
            float: Unified overall risk score (0.0 to 1.0)
        """
        # A3: V2 GNN fusion — when GNN score is available use the new formula
        if gnn_score is not None:
            gnn_normalized = max(0.0, min(1.0, gnn_score / 100.0))
            return (rule_score * 0.3) + (ml_score * 0.3) + (gnn_normalized * 0.4)

        # Legacy 3-component weighted average (unchanged)
        w_rule = self.weights.get("rule_engine", 0.0)
        w_ml = self.weights.get("isolation_forest", 0.0)
        w_beh = self.weights.get("behavioural", 0.0)

        raw_score = (rule_score * w_rule) + (ml_score * w_ml) + (behavioral_score * w_beh)
        weight_sum = w_rule + w_ml + w_beh

        return (raw_score / weight_sum) if weight_sum > 0 else 0.0


    def get_weights(self) -> Dict[str, float]:
        """Returns active fusion weights.

        Returns:
            Dict[str, float]: Configured weights.
        """
        return self.weights

    def _validate_weights(self) -> None:
        """Validates that weights sum to approximately 1.0 and are non-negative."""
        w_sum = sum(self.weights.values())
        if not (0.95 <= w_sum <= 1.05):
            raise ValueError(f"Fusion weights must sum to approximately 1.0, got {w_sum}")
        for k, v in self.weights.items():
            if v < 0:
                raise ValueError(f"Fusion weight for '{k}' cannot be negative, got {v}")
