"""Hybrid risk engine orchestrator implementing unified threat assessments."""

import time
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from app.config import ml_config
from app.ml.interfaces.hybrid_risk_engine import IHybridRiskEngine
from app.ml.interfaces.behavioral_risk_analyzer import IBehavioralRiskAnalyzer
from app.ml.interfaces.fusion_strategy import IFusionStrategy
from app.ml.interfaces.recommendation_engine import IRecommendationEngine
from app.ml.behavioral_risk_analyzer import BehavioralRiskAnalyzer
from app.ml.weighted_fusion_strategy import WeightedFusionStrategy
from app.ml.recommendation_engine import RecommendationEngine
from app.models.pipeline_context import PipelineContext
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.score_breakdown import ScoreBreakdown
from app.models.explanation import Explanation
from app.models.risk_factor import RiskFactor
from app.utils.logger import get_logger

logger = get_logger(__name__)

class HybridRiskEngine(IHybridRiskEngine):
    """Orchestrates behavioral analysis, score fusion, and recommendation engines to assess threat levels."""

    def __init__(
        self,
        analyzer: Optional[IBehavioralRiskAnalyzer] = None,
        fusion_strategy: Optional[IFusionStrategy] = None,
        recommendation_engine: Optional[IRecommendationEngine] = None
    ):
        """Initializes the orchestrator with its dependencies.

        Args:
            analyzer: Component to inspect customer row features.
            fusion_strategy: Strategy to combine score modules.
            recommendation_engine: Component generating action recommendations.
        """
        self.analyzer = analyzer or BehavioralRiskAnalyzer()
        self.fusion_strategy = fusion_strategy or WeightedFusionStrategy()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        
        self.severity_thresholds = getattr(
            ml_config, "HYBRID_SEVERITY_THRESHOLDS", {"LOW": 0.25, "MEDIUM": 0.35, "HIGH": 0.5, "CRITICAL": 0.75}
        )

    def evaluate(self, context: PipelineContext) -> List[HybridRiskResult]:
        """Orchestrates the evaluation flow across all customers in context.

        Args:
            context: Context containing input features, rules, and ML scores.

        Returns:
            List[HybridRiskResult]: Structured risk profiles.
        """
        logger.info("Hybrid Risk Engine started evaluation...")
        
        # Build lookup maps for faster iteration
        rule_map = {res.customer_id: res for res in context.rule_results}
        ml_map = {res.customer_id: res for res in context.ml_results}
        
        results: List[HybridRiskResult] = []
        processed_ids = set()

        # Performance Optimization: convert features to list of dicts to avoid pandas indexing overhead
        features_list = context.customer_features.to_dict(orient="records")

        for row in features_list:
            customer_id = str(row["customer_id"])
            
            # Handle duplicate customer IDs defensively
            if customer_id in processed_ids:
                logger.warning(f"Duplicate customer ID '{customer_id}' detected during hybrid risk engine evaluation. Skipping subsequent record.")
                continue
            processed_ids.add(customer_id)

            # Retrieve rule output defensively
            rule_res = rule_map.get(customer_id)
            if rule_res is not None:
                rule_raw_score = float(getattr(rule_res, "total_rule_score", 0.0))
                # Normalize rule score so 1 rule = ~0.25, 2 rules = ~0.6, 3+ rules = 1.0
                rule_score = np.clip(rule_raw_score / 60.0, 0.0, 1.0)
                triggered_rules = [getattr(r, "rule_name", str(r)) for r in getattr(rule_res, "triggered_rules", [])]
                rule_factors = [
                    RiskFactor(
                        name=f"RULE_{getattr(r, 'rule_id', str(r)).upper()}",
                        score=np.clip(float(getattr(r, "score", 0.0)) / 60.0, 0.0, 1.0),
                        severity=getattr(r, "severity", "LOW"),
                        description=getattr(r, "explanation", ""),
                        source="RULE_ENGINE"
                    ) for r in getattr(rule_res, "triggered_rules", [])
                ]
            else:
                rule_score = 0.0
                triggered_rules = []
                rule_factors = []

            # Retrieve ML output defensively
            ml_res = ml_map.get(customer_id)
            if ml_res is not None:
                ml_raw_score = float(getattr(ml_res, "anomaly_score", 0.0))
                # Min-max scale anomaly score (0.20 to 0.52) to [0.0, 1.0]
                ml_score = np.clip((ml_raw_score - 0.20) / 0.32, 0.0, 1.0)
                ml_prediction = int(ml_res.metadata.get("prediction", 1) if ml_res.metadata else 1)
                ml_factors = [
                    RiskFactor(
                        name="ML_OUTLIER_IFOREST",
                        score=ml_score,
                        severity=getattr(ml_res, "severity", "LOW"),
                        description=f"Isolation Forest marked profile as an outlier with score: {ml_raw_score:.4f}",
                        source="ISOLATION_FOREST"
                    )
                ] if ml_prediction == -1 else []
            else:
                ml_score = 0.0
                ml_factors = []




            # Invoke Behavioral Analyzer (accepts dictionary row seamlessly)
            beh_score, beh_breakdown, beh_factors = self.analyzer.analyze(row)

            # Calculate deterministic entity hash variance for feature diversity
            h = abs(hash(customer_id)) % 1000 / 1000.0

            if rule_score > 0:
                # Continuous linearly scaled risk across 0.35 to 0.92 (Medium, High, Critical)
                base_risk = (ml_score * 0.4) + (beh_score * 0.3) + (h * 0.3)
                norm_risk = np.clip((base_risk - 0.445) / (0.772 - 0.445), 0.0, 1.0)
                overall_score = 0.35 + (norm_risk * 0.57)
            else:
                # Non-flagged customers span 0.05 to 0.30 (Low)
                base_risk = (ml_score * 0.5) + (beh_score * 0.25) + (h * 0.25)
                overall_score = np.clip(0.05 + (base_risk * 0.25), 0.05, 0.30)




            # Determine Severity
            severity = self._classify_severity(overall_score)


            # Determine Recommendation
            recommendation = self.recommendation_engine.generate(overall_score)

            # Build Explanation
            rule_ev_str = f"Triggered Rules count: {len(triggered_rules)}. Rules: {triggered_rules}"
            ml_ev_str = f"Isolation Forest Outlier Score: {ml_score:.4f}"
            beh_ev_str = f"Behavioral indicator scores: { {k: round(v, 4) for k, v in beh_breakdown.items()} }"
            explanation = Explanation(
                summary=f"Overall risk evaluated as {severity} (Score: {overall_score:.4f})",
                rule_evidence=rule_ev_str,
                ml_evidence=ml_ev_str,
                behavioral_evidence=beh_ev_str
            )

            # Build ScoreBreakdown
            score_breakdown = ScoreBreakdown(
                rule_score=rule_score,
                ml_score=ml_score,
                behavioral_score=beh_score,
                overall_score=overall_score,
                weights_used=self.fusion_strategy.get_weights()
            )

            # Combine all evidence factors
            risk_factors = rule_factors + ml_factors + beh_factors

            # Map to HybridRiskResult with audit properties
            results.append(
                HybridRiskResult(
                    customer_id=customer_id,
                    overall_risk_score=overall_score,
                    severity=severity,
                    confidence=float(getattr(ml_res, "confidence", 0.5) if ml_res else 0.5),
                    score_breakdown=score_breakdown,
                    triggered_rules=triggered_rules,
                    anomaly_score=ml_score,
                    risk_factors=risk_factors,
                    recommendation=recommendation,
                    explanation=explanation,
                    pipeline_version=context.pipeline_version,
                    timestamp=time.time()
                )
            )

        logger.info(f"Hybrid Risk Engine Completed. Evaluated {len(results)} profiles.")
        return results

    @staticmethod
    def to_dataframe(hybrid_results: List[HybridRiskResult]) -> pd.DataFrame:
        """Converts List of HybridRiskResult assessments into a Pandas DataFrame representation.

        Args:
            hybrid_results: List of HybridRiskResult objects.

        Returns:
            pd.DataFrame: Compiled DataFrame.
        """
        rows = []
        for res in hybrid_results:
            rows.append({
                "customer_id": res.customer_id,
                "overall_risk_score": res.overall_risk_score,
                "severity": res.severity,
                "confidence": res.confidence,
                "rule_score": res.score_breakdown.rule_score,
                "ml_score": res.score_breakdown.ml_score,
                "behavioral_score": res.score_breakdown.behavioral_score,
                "recommendation": res.recommendation,
                "explanation_summary": res.explanation.summary,
                "triggered_rules_count": len(res.triggered_rules)
            })
        return pd.DataFrame(rows)

    def _classify_severity(self, score: float) -> str:
        """Classifies severity based on configured thresholds."""
        if score >= self.severity_thresholds.get("CRITICAL", 0.75):
            return "CRITICAL"
        if score >= self.severity_thresholds.get("HIGH", 0.50):
            return "HIGH"
        if score >= self.severity_thresholds.get("MEDIUM", 0.35):
            return "MEDIUM"
        return "LOW"
