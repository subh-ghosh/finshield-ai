"""Planner context output format serializer implementation returning token-efficient reports for AI models."""

from typing import Any, Dict
from app.explainability.interfaces.i_output_serializer import IOutputSerializer
from app.models.explanation_response import ExplanationResponseV1

class PlannerContextSerializer(IOutputSerializer):
    """Compresses ExplanationResponseV1 inputs into dense data mappings to feed LangGraph AI Planner contexts."""

    def serialize(self, response: ExplanationResponseV1) -> Dict[str, Any]:
        """Transforms response to compressed AI model friendly format.

        Args:
            response: Consolidated ExplanationResponseV1.

        Returns:
            Dict[str, Any]: Compiled context mapping.
        """
        top_traces = []
        for item in response.evidence[:5]:
            top_traces.append({
                "source": item.source,
                "title": item.title,
                "trace_id": item.rule_id or item.anomaly_id,
                "score": round(item.score, 4),
                "severity": item.severity
            })
            
        return {
            "customer_id": response.customer_id,
            "overall_risk_score": round(response.overall_risk_score, 4),
            "severity": response.severity,
            "confidence": round(response.confidence, 4),
            "recommendation": response.recommendation,
            "summary_narrative": response.summary,
            "score_breakdown": {k: round(v, 4) for k, v in response.risk_breakdown.items()},
            "critical_traces": top_traces,
            "timeline_length": len(response.timeline)
        }

    def get_format_name(self) -> str:
        """Returns format name identifier."""
        return "planner"
