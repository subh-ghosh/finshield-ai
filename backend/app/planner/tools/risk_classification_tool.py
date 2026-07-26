"""Tool: GET /api/v1/risk-classify/{customer_id} — hybrid risk classification."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class RiskClassificationTool(BaseTool):
    """Returns full hybrid risk classification for a customer.

    Combines rule engine (0.3) + Isolation Forest (0.3) + GNN (0.4) into:
    - risk_score_pct: 0-100
    - risk_category: LOW / MEDIUM / HIGH / CRITICAL
    - recommendation: MONITOR / MANUAL_REVIEW / ESCALATE / FILE_SAR

    Use for queries like:
    - "Classify the risk level of C_1"
    - "What is the risk category for this customer?"
    - "Should we escalate customer C_500?"
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="risk_classification",
            description=(
                "Returns full hybrid risk classification for a customer: "
                "risk_score_pct (0-100), risk_category (LOW/MEDIUM/HIGH/CRITICAL), "
                "severity, rule contributions, ML contributions, and recommended escalation "
                "(MONITOR / MANUAL_REVIEW / ESCALATE / FILE_SAR). "
                "Use as the final step after feature_engineering and anomaly_detection."
            ),
            endpoint="/api/v1/risk-classify/{customer_id}",
            http_method="GET",
            input_schema={"customer_id": "str"},
            output_schema={
                "risk_score_pct": "float (0-100)",
                "risk_category": "str (LOW/MEDIUM/HIGH/CRITICAL)",
                "recommendation": "str",
                "rule_contribution": "dict",
                "ml_contribution": "dict",
            }
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/risk-classify/{customer_id}.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            Full risk classification dict.
        """
        return await client.get_risk_classification(customer_id)
