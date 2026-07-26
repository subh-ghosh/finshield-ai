"""AI-driven rule suggestion engine — proposes new deterministic rules.

Analyzes feature distributions to find where high-anomaly customers 
cluster at extreme values, and proposes threshold rules for human review.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RuleSuggestion:
    """A single AI-suggested AML rule for human approval."""
    name: str
    description: str
    column: str
    operator: str
    threshold: float
    confidence: float  # 0.0 - 1.0
    status: str = "PENDING"  # PENDING | APPROVED | REJECTED

    def to_dict(self) -> dict:
        return asdict(self)


class RuleSuggestionEngine:
    """Analyzes feature distributions to suggest new AML rules.
    
    Finds numeric columns where high-risk customers cluster at extreme
    values (above the 95th percentile of normal customers) and proposes
    threshold-based rules for human review.
    """

    def __init__(self):
        self._approved_rules: Dict[str, RuleSuggestion] = {}
        self._suggestions_cache: Optional[List[RuleSuggestion]] = None

    def suggest_rules(self, features_df: pd.DataFrame,
                      anomaly_scores: Dict[str, float]) -> List[RuleSuggestion]:
        """Generate rule suggestions based on feature analysis.
        
        Args:
            features_df: Customer feature DataFrame (must contain 'customer_id').
            anomaly_scores: Dict mapping customer_id → risk score (0-100).
            
        Returns:
            Top-10 highest-confidence rule suggestions.
        """
        suggestions: List[RuleSuggestion] = []

        # Identify high-risk customers (score > 50 maps to MEDIUM+ in hybrid engine)
        high_risk_ids = {str(cid) for cid, score in anomaly_scores.items() if score > 50}

        if len(high_risk_ids) < 3:
            logger.info("Too few high-risk customers for rule suggestion analysis.")
            self._suggestions_cache = []
            return []

        # Ensure customer_id is a string column
        df = features_df.copy()
        if "customer_id" in df.columns:
            df["customer_id"] = df["customer_id"].astype(str)
        else:
            df = df.reset_index()
            df.rename(columns={df.columns[0]: "customer_id"}, inplace=True)
            df["customer_id"] = df["customer_id"].astype(str)

        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "customer_id"]

        for col in numeric_cols:
            try:
                high_risk_vals = df[df["customer_id"].isin(high_risk_ids)][col].dropna()
                normal_vals = df[~df["customer_id"].isin(high_risk_ids)][col].dropna()

                if len(high_risk_vals) < 3 or len(normal_vals) < 3:
                    continue

                # If high-risk customers are above the 95th percentile of normals
                p95 = normal_vals.quantile(0.95)
                if p95 == 0:
                    continue

                pct_above = (high_risk_vals > p95).mean()

                if pct_above > 0.7:  # 70%+ of high-risk exceed this threshold
                    clean_name = col.replace("_", " ").title()
                    suggestions.append(RuleSuggestion(
                        name=f"Auto_{col}_Threshold",
                        description=(
                            f"Flag customers where {clean_name} > {p95:.2f} "
                            f"(95th percentile). {pct_above * 100:.0f}% of "
                            f"high-risk customers exceed this."
                        ),
                        column=col,
                        operator=">",
                        threshold=float(p95),
                        confidence=float(pct_above)
                    ))
            except Exception as e:
                logger.debug(f"Skipping column {col} for rule suggestion: {e}")
                continue

        # Sort by confidence, take top 10
        suggestions = sorted(suggestions, key=lambda s: s.confidence, reverse=True)[:10]
        self._suggestions_cache = suggestions

        logger.info(f"Generated {len(suggestions)} rule suggestions.")
        return suggestions

    def approve_rule(self, rule_name: str) -> Optional[RuleSuggestion]:
        """Approve a suggested rule by name.
        
        Returns the approved rule, or None if not found.
        """
        if self._suggestions_cache is None:
            return None

        for s in self._suggestions_cache:
            if s.name == rule_name:
                s.status = "APPROVED"
                self._approved_rules[rule_name] = s
                logger.info(f"Rule '{rule_name}' approved by analyst.")
                return s
        return None

    def reject_rule(self, rule_name: str) -> Optional[RuleSuggestion]:
        """Reject a suggested rule by name."""
        if self._suggestions_cache is None:
            return None

        for s in self._suggestions_cache:
            if s.name == rule_name:
                s.status = "REJECTED"
                return s
        return None

    def get_approved_rules(self) -> List[RuleSuggestion]:
        """Return all analyst-approved rules."""
        return list(self._approved_rules.values())

    def clear_cache(self) -> None:
        """Reset suggestions cache to force re-analysis."""
        self._suggestions_cache = None
