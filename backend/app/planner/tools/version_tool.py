"""Tool: GET /api/v1/version — backend version and compatibility metadata."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class VersionTool(BaseTool):
    """Retrieves backend service version for compatibility verification."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="version",
            description="Retrieve backend service version and API compatibility information. Use to verify planner/backend compatibility.",
            endpoint="/api/v1/version",
            http_method="GET",
            input_schema={},
            output_schema={"service": "str", "version": "str", "api_version": "str", "schema_version": "str"}
        )

    async def execute(self, client: Any, **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/version.

        Args:
            client: FinShieldAPIClient instance.

        Returns:
            Version metadata dict.
        """
        return await client.get_version()
