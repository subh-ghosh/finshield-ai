"""Central tool registry with metadata support and auto-registration."""

from typing import Dict, List, Optional
from app.planner.tools.base_tool import BaseTool, ToolMetadata
from app.planner.tools.analyze_customer_tool import AnalyzeCustomerTool
from app.planner.tools.analyze_batch_tool import AnalyzeBatchTool
from app.planner.tools.anomaly_detection_tool import AnomalyDetectionTool
from app.planner.tools.eda_analysis_tool import EDAAnalysisTool
from app.planner.tools.feature_engineering_tool import FeatureEngineeringTool
from app.planner.tools.get_customer_profile_tool import GetCustomerProfileTool
from app.planner.tools.get_explanation_tool import GetExplanationTool
from app.planner.tools.health_tool import HealthTool
from app.planner.tools.risk_classification_tool import RiskClassificationTool
from app.planner.tools.version_tool import VersionTool
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """Central registry mapping tool names to BaseTool instances and ToolMetadata.

    Supports:
    - get_tool(name): Returns BaseTool instance
    - list_tools(): Returns list of registered tool names
    - get_metadata(name): Returns ToolMetadata descriptor
    - register(tool): Registers a new tool instance
    """

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._metadata: Dict[str, ToolMetadata] = {}

    def register(self, tool: BaseTool) -> None:
        """Registers a tool instance and its metadata.

        Args:
            tool: BaseTool instance to register.
        """
        meta = tool.metadata
        self._tools[meta.name] = tool
        self._metadata[meta.name] = meta
        logger.info(f"ToolRegistry: Registered tool '{meta.name}' → {meta.http_method} {meta.endpoint}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Returns a registered BaseTool instance by name.

        Args:
            name: Registered tool name.

        Returns:
            BaseTool instance or None if not found.
        """
        tool = self._tools.get(name)
        if tool is None:
            logger.warning(f"ToolRegistry: Tool '{name}' not found in registry.")
        return tool

    def list_tools(self) -> List[str]:
        """Returns list of all registered tool names.

        Returns:
            List[str]: Sorted list of tool names.
        """
        return sorted(self._tools.keys())

    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Returns ToolMetadata descriptor for a registered tool.

        Args:
            name: Registered tool name.

        Returns:
            ToolMetadata or None if not found.
        """
        return self._metadata.get(name)

    def list_metadata(self) -> List[ToolMetadata]:
        """Returns all ToolMetadata descriptors for all registered tools.

        Returns:
            List[ToolMetadata]: All tool metadata records.
        """
        return list(self._metadata.values())


def build_registry() -> ToolRegistry:
    """Builds and returns a fully populated ToolRegistry with all tools registered.

    Returns:
        ToolRegistry: Populated registry instance.
    """
    registry = ToolRegistry()
    for tool in [
        # 5 core tools matching the problem statement's required agent architecture
        EDAAnalysisTool(),              # EDA Tool
        FeatureEngineeringTool(),       # Feature Engineering Tool
        AnomalyDetectionTool(),         # Anomaly Detection Tool
        RiskClassificationTool(),       # Risk Classification Tool
        GetExplanationTool(),           # Explanation Component
        # Supporting tools
        AnalyzeCustomerTool(),
        AnalyzeBatchTool(),
        GetCustomerProfileTool(),
        HealthTool(),
        VersionTool(),
    ]:
        registry.register(tool)
    return registry


# Module-level singleton registry
TOOL_REGISTRY: ToolRegistry = build_registry()
