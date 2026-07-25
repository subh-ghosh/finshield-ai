"""Tool: GET /api/v1/customer/{id} — customer feature profile retrieval."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class GetCustomerProfileTool(BaseTool):
    """Retrieves cached customer engineered feature profile from REST API."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_customer_profile",
            description="Retrieves cached customer feature metrics, rule summary, and anomaly score.",
            endpoint="/api/v1/customer/{customer_id}",
            http_method="GET",
            input_schema={"customer_id": "str"},
            output_schema={"customer_id": "str", "feature_metrics": "dict",
                           "rule_summary": "dict", "anomaly_summary": "dict"}
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/customer/{customer_id}.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            CustomerProfileResponse as dict.
        """
        return await client.get_customer(customer_id)
