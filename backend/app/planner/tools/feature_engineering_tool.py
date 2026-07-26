"""Tool: GET /api/v1/features/{customer_id} — AML feature engineering for a customer."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class FeatureEngineeringTool(BaseTool):
    """Retrieves engineered AML feature vector for a customer.

    Use for queries like:
    - "Find structuring patterns in the last 30 days" (needs feature vector first)
    - "Show me the velocity features for C_1"
    - "What are the AML signals for customer C_500?"
    - Automatically invoked before anomaly detection for targeted queries
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="feature_engineering",
            description=(
                "Computes and returns the AML feature vector for a specific customer: "
                "transaction velocity, rolling 24h sums, structuring score, smurfing score, "
                "cash-out ratio, amount deviation, and network risk. "
                "Use before anomaly_detection for targeted single-customer or pattern queries. "
                "Do NOT use for broad dataset queries — use eda_analysis instead."
            ),
            endpoint="/api/v1/features/{customer_id}",
            http_method="GET",
            input_schema={"customer_id": "str"},
            output_schema={
                "velocity_features": "dict",
                "amount_features": "dict",
                "pattern_features": "dict",
                "network_features": "dict",
            }
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/features/{customer_id}.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            AML feature vector grouped by category.
        """
        return await client.get_customer_features(customer_id)
