"""Hybrid risk engine orchestrator abstract interface contract definition."""

from abc import ABC, abstractmethod
from typing import List
from app.models.pipeline_context import PipelineContext
from app.models.hybrid_risk_result import HybridRiskResult

class IHybridRiskEngine(ABC):
    """Interface defining the primary orchestrator that aggregates results into HybridRiskResult listings."""

    @abstractmethod
    def evaluate(self, context: PipelineContext) -> List[HybridRiskResult]:
        """Orchestrates sub-analyzers and fusion strategies to build customer results.

        Args:
            context: Context details (features, rules results, ML outputs).

        Returns:
            List[HybridRiskResult]: Fused assessment result details.
        """
        pass
