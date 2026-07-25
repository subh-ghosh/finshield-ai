"""Interface contract definition for Explainability Service orchestrators."""

from abc import ABC, abstractmethod
from app.models.explainability_context import ExplainabilityContext
from app.models.explanation_response import ExplanationResponseV1

class IExplainabilityService(ABC):
    """Abstract orchestrator interface executing the end-to-end explainability pipeline."""

    @abstractmethod
    def explain(self, context: ExplainabilityContext) -> ExplanationResponseV1:
        """Transforms a hybrid assessment context into a versioned response.

        Args:
            context: Execution context containing features, results, and config options.

        Returns:
            ExplanationResponseV1: Consolidated case explanation response.
        """
        pass
