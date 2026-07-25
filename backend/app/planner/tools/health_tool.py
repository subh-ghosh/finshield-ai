"""Tool: GET /api/v1/health — backend service health check."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class HealthTool(BaseTool):
    """Checks REST API service health status."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="health",
            description="Checks REST API service availability and health status.",
            endpoint="/api/v1/health",
            http_method="GET",
            input_schema={},
            output_schema={"status": "str", "service": "str", "version": "str", "uptime_seconds": "float"}
        )

    async def execute(self, client: Any, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/health.

        Args:
            client: FinShieldAPIClient instance.

        Returns:
            HealthResponse as dict.
        """
        return await client.health()
