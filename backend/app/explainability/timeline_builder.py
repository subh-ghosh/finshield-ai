"""Timeline builder implementation compiling chronological investigation timelines."""

import time
from typing import Any, Dict, List
from app.explainability.interfaces.i_timeline_builder import ITimelineBuilder
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.timeline_event import TimelineEvent

class TimelineBuilder(ITimelineBuilder):
    """Generates sequential timeline logs tracing case evaluations from ingestion to recommendations."""

    def build_timeline(self, hybrid_result: HybridRiskResult, metadata: Dict[str, Any]) -> List[TimelineEvent]:
        """Builds timeline list based on hybrid risk result properties.

        Args:
            hybrid_result: Unified assessment risk profile.
            metadata: Pipeline execution parameters.

        Returns:
            List[TimelineEvent]: Chronological timeline.
        """
        timeline: List[TimelineEvent] = []
        
        # Use active timestamp or default to current epoch
        base_time = float(getattr(hybrid_result, "timestamp", time.time()))
        if base_time == 0.0:
            base_time = time.time()
            
        # Chronological event sequence
        timeline.append(
            TimelineEvent(
                event_name="Feature Engineering Completed",
                timestamp=base_time - 2.5,
                severity="LOW",
                description="Ingested transactional ledger and computed customer behavioral metrics.",
                source="SYSTEM"
            )
        )
        
        rules_triggered_count = len(hybrid_result.triggered_rules)
        rules_desc = (
            f"Rule violations triggered: {hybrid_result.triggered_rules}"
            if rules_triggered_count > 0 else "Zero rules triggered."
        )
        timeline.append(
            TimelineEvent(
                event_name="Rule Evaluation Finished",
                timestamp=base_time - 2.0,
                severity="HIGH" if rules_triggered_count > 0 else "LOW",
                description=f"Rule Engine finished run. {rules_desc}",
                source="RULE_ENGINE"
            )
        )
        
        is_anomaly = hybrid_result.anomaly_score >= 0.5
        timeline.append(
            TimelineEvent(
                event_name="Isolation Forest Outlier Checked",
                timestamp=base_time - 1.5,
                severity="HIGH" if is_anomaly else "LOW",
                description=f"ML outlier model evaluated score of {hybrid_result.anomaly_score:.4f}.",
                source="ISOLATION_FOREST"
            )
        )
        
        timeline.append(
            TimelineEvent(
                event_name="Hybrid Risk Aggregated",
                timestamp=base_time - 1.0,
                severity=hybrid_result.severity,
                description=f"Unified score computed via weighted strategy. Fused overall score: {hybrid_result.overall_risk_score:.4f}.",
                source="HYBRID_RISK_ENGINE"
            )
        )
        
        timeline.append(
            TimelineEvent(
                event_name="Compliance Case Recommendation Issued",
                timestamp=base_time,
                severity="CRITICAL" if hybrid_result.severity in ["HIGH", "CRITICAL"] else "LOW",
                description=f"Generated recommendation status: {hybrid_result.recommendation}",
                source="RECOMMENDATION_ENGINE"
            )
        )
        
        return timeline
