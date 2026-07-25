"""Tool: POST /api/v1/analyze/batch — batch customer risk analysis."""

from typing import Any, Dict, List
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class AnalyzeBatchTool(BaseTool):
    """Analyzes multiple customers in a single batch request via REST API."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="analyze_batch",
            description="Runs AML risk analysis for multiple customer IDs in a single batch. Returns list of ExplanationResponseV1.",
            endpoint="/api/v1/analyze/batch",
            http_method="POST",
            input_schema={"customer_ids": "list[str]"},
            output_schema={"reports": "list[ExplanationResponseV1]"}
        )

    async def execute(self, client: Any, customer_ids: List[str], **kwargs: Any) -> Dict[str, Any]:
        """Calls POST /api/v1/analyze/batch.

        Args:
            client: FinShieldAPIClient instance.
            customer_ids: List of customer identifiers.

        Returns:
            List of ExplanationResponseV1 as dicts.
        """
        results = await client.analyze_batch(customer_ids)
        return {"reports": results, "count": len(results)}
