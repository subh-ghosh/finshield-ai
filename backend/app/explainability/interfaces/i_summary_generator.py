"""Interface contract definition for Summary Generator services."""

from abc import ABC, abstractmethod
from app.models.explainability_context import ExplainabilityContext
from app.models.investigation_summary import InvestigationSummary

class ISummaryGenerator(ABC):
    """Abstract contract responsible for producing natural language investigator summaries."""

    @abstractmethod
    def generate_summary(self, context: ExplainabilityContext) -> InvestigationSummary:
        """Translates risk numbers into a readable case summary.

        Args:
            context: Consolidated explainability call context.

        Returns:
            InvestigationSummary: Written summary reports.
        """
        pass
