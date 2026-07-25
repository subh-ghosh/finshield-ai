"""Interface contract definition for Explainability Output Serializers."""

from abc import ABC, abstractmethod
from typing import Any
from app.models.explanation_response import ExplanationResponseV1

class IOutputSerializer(ABC):
    """Abstract contract translating domain responses into target formats (JSON, Markdown, Plain Text, Planner)."""

    @abstractmethod
    def serialize(self, response: ExplanationResponseV1) -> Any:
        """Transforms explanation details into serialized structures.

        Args:
            response: Consolidated V1 explanation response.

        Returns:
            Any: Serialized output data.
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """Returns the format name identifier (e.g. 'json', 'markdown', 'text', 'planner')."""
        pass
