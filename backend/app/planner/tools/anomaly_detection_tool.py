"""Tool: GET /api/v1/anomaly/{customer_id} — Isolation Forest anomaly scoring."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class AnomalyDetectionTool(BaseTool):
    """Runs ML-based anomaly detection (Isolation Forest) for a customer.

    Use for queries like:
    - "Is customer C_1 suspicious?"
    - "Flag high-risk customers"
    - "Detect anomalous transaction patterns"
    - "Run anomaly detection on C_500"
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="anomaly_detection",
            description=(
                "Runs Isolation Forest anomaly detection for a specific customer. "
                "Returns anomaly_score (0.0-1.0, higher=more suspicious), prediction (-1=anomaly), "
                "severity, confidence, and pattern interpretation. "
                "Best used after feature_engineering for targeted queries. "
                "For top anomalous customers across the dataset, use eda_analysis instead."
            ),
            endpoint="/api/v1/anomaly/{customer_id}",
            http_method="GET",
            input_schema={"customer_id": "str"},
            output_schema={
                "anomaly_score": "float (0.0-1.0)",
                "prediction": "int (-1=anomaly, 1=normal)",
                "severity": "str",
                "confidence": "float",
                "is_anomaly": "bool",
                "interpretation": "str",
            }
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/anomaly/{customer_id}.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            Anomaly detection result dict.
        """
        return await client.get_customer_anomaly(customer_id)
