"""JSON output format serializer implementation converting models to dictionaries."""

import dataclasses
from typing import Any, Dict
from app.explainability.interfaces.i_output_serializer import IOutputSerializer
from app.models.explanation_response import ExplanationResponseV1

class JSONSerializer(IOutputSerializer):
    """Converts ExplanationResponseV1 instances into JSON-compatible nested dictionaries."""

    def serialize(self, response: ExplanationResponseV1) -> Dict[str, Any]:
        """Transforms response to a dictionary representation.

        Args:
            response: Consolidated ExplanationResponseV1.

        Returns:
            Dict[str, Any]: Serialized dictionary mapping.
        """
        return dataclasses.asdict(response)

    def get_format_name(self) -> str:
        """Returns format name identifier."""
        return "json"
