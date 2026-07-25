"""Tool: GET /api/v1/explanation/{id} — direct ExplanationResponseV1 retrieval."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class GetExplanationTool(BaseTool):
    """Retrieves ExplanationResponseV1 report for a customer via REST API."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="get_explanation",
            description="Retrieves the full ExplanationResponseV1 report for a customer. Includes evidence, timeline, and recommendations.",
            endpoint="/api/v1/explanation/{customer_id}",
            http_method="GET",
            input_schema={"customer_id": "str"},
            output_schema={"response_id": "str", "customer_id": "str", "overall_risk_score": "float",
                           "severity": "str", "evidence": "list", "timeline": "list",
                           "metadata": "dict", "metrics": "dict"}
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/explanation/{customer_id}.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            ExplanationResponseV1 as dict.
        """
        return await client.get_explanation(customer_id)
