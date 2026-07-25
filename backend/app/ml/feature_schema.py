"""Simple feature schema representation and input validation class."""

from typing import Dict, List
import pandas as pd
from app.ml.exceptions import InvalidFeatureSchemaException

class FeatureSchema:
    """Represents the expected feature names and types, validating inputs against them."""

    def __init__(self, feature_names: List[str], data_types: Dict[str, str]):
        """Initializes FeatureSchema.

        Args:
            feature_names: List of expected column names in correct order.
            data_types: Dict mapping column names to general types (e.g., 'numeric').
        """
        self.feature_names = feature_names
        self.data_types = data_types

    def validate(self, df: pd.DataFrame) -> None:
        """Validates that the input DataFrame complies with the expected feature list and types.

        Args:
            df: The incoming DataFrame to validate.

        Raises:
            InvalidFeatureSchemaException: If a validation check fails.
        """
        # Validate column presence
        missing = [col for col in self.feature_names if col not in df.columns]
        if missing:
            raise InvalidFeatureSchemaException(f"Required columns missing from dataset: {missing}")

        # Validate column data types
        for col, expected_type in self.data_types.items():
            if expected_type == "numeric":
                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise InvalidFeatureSchemaException(
                        f"Feature column '{col}' is expected to be numeric, but got {df[col].dtype}"
                    )
            elif expected_type not in str(df[col].dtype):
                raise InvalidFeatureSchemaException(
                    f"Feature column '{col}' type mismatch. Expected: {expected_type}, Got: {df[col].dtype}"
                )
