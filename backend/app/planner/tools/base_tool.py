"""Abstract base class for all planner REST API tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolMetadata:
    """Metadata descriptor for a registered planner tool."""
    name: str
    description: str
    endpoint: str
    http_method: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)


class BaseTool(ABC):
    """Abstract base tool delegating all HTTP calls to FinShieldAPIClient."""

    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        """Returns tool metadata descriptor."""

    @abstractmethod
    async def execute(self, client: Any, **kwargs: Any) -> Dict[str, Any]:
        """Executes the tool using the shared async API client.

        Args:
            client: FinShieldAPIClient instance (async context manager already entered).
            **kwargs: Tool-specific parameters.

        Returns:
            Dict containing tool output.
        """
