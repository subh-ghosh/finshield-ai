"""Tool: POST /api/v1/analyze/customer — single customer risk analysis."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class AnalyzeCustomerTool(BaseTool):
    """Analyzes a single customer through the full AML pipeline via REST API."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="analyze_customer",
            description="Runs full AML risk analysis for a single customer ID. Returns ExplanationResponseV1.",
            endpoint="/api/v1/analyze/customer",
            http_method="POST",
            input_schema={"customer_id": "str"},
            output_schema={"customer_id": "str", "overall_risk_score": "float", "severity": "str",
                           "recommendation": "str", "evidence": "list", "explanation": "dict"}
        )

    async def execute(self, client: Any, customer_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Calls POST /api/v1/analyze/customer.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Target customer identifier.

        Returns:
            ExplanationResponseV1 as dict.
        """
        if customer_id.startswith("CUST-"):
            customer_id = customer_id.replace("CUST-", "C_")
        return await client.analyze_customer(customer_id)
