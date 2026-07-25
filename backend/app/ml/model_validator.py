"""Validation checks verifying shape, NaN, and Infinite inputs prior to inference."""

from typing import List
import numpy as np
import pandas as pd
from app.ml.exceptions import InvalidFeatureSchemaException, PredictionException

class ModelValidator:
    """Ensures input DataFrames comply with feature constraints, ordering, and value ranges."""

    @staticmethod
    def validate_features(df: pd.DataFrame, expected_features: List[str]) -> None:
        """Validates features before running inference.

        Args:
            df: Selected features DataFrame to inspect.
            expected_features: List of expected feature columns in correct order.

        Raises:
            InvalidFeatureSchemaException: If required columns, ordering, or dimensions mismatch.
            PredictionException: If NaN or infinite values are found in the matrix.
        """
        # Check required columns count and presence
        missing = [col for col in expected_features if col not in df.columns]
        if missing:
            raise InvalidFeatureSchemaException(f"Required features missing: {missing}")

        # Check feature dimensions mismatch
        if len(df.columns) != len(expected_features):
            raise InvalidFeatureSchemaException(
                f"Feature dimension mismatch. Expected: {len(expected_features)}, Got: {len(df.columns)}"
            )

        # Check feature ordering
        for i, col in enumerate(df.columns):
            if col != expected_features[i]:
                raise InvalidFeatureSchemaException(
                    f"Feature ordering mismatch at position {i}. Expected: '{expected_features[i]}', Got: '{col}'"
                )

        # Check for NaN values
        if df.isnull().any().any():
            raise PredictionException("Inference feature matrix contains NaN values.")

        # Check for Infinite values
        if np.isinf(df.select_dtypes(include=[np.number]).values).any():
            raise PredictionException("Inference feature matrix contains Infinite values.")
