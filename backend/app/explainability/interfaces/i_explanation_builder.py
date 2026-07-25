"""Interface contract definition for Explanation Builder structural services."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.explainability_context import ExplainabilityContext

class IExplanationBuilder(ABC):
    """Abstract contract responsible for parsing evidence data structures into structured JSON reports."""

    @abstractmethod
    def build(self, context: ExplainabilityContext) -> Dict[str, Any]:
        """Arranges metrics, indicators, and details into structured dictionary mappings.

        Args:
            context: Consolidated explainability call context.

        Returns:
            Dict[str, Any]: Structured explainability JSON mapping.
        """
        pass
