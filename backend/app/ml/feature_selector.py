"""Feature selection component isolating numeric behavioural column extractions.

This class decouples model architectures from pandas features, enabling future 
variance or correlation filters without altering inference flows.
"""

from typing import Any, List, Optional
import pandas as pd
from app.config import ml_config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureSelector:
    """Selects and validates numeric behavioral columns for ML models."""

    def __init__(self, feature_columns: Optional[List[str]] = None):
        """Initializes FeatureSelector.

        Args:
            feature_columns: Optional explicit list of columns to select.
        """
        self.feature_columns = feature_columns or ml_config.FEATURE_COLUMNS

    def fit(self, df: pd.DataFrame, y: Optional[Any] = None) -> "FeatureSelector":
        """Fits the feature selector on input data.

        Args:
            df: Customer features DataFrame.
            y: Ignored target labels.

        Returns:
            FeatureSelector: Self instance.
        """
        # Validate that required features exist in the DataFrame
        missing = [col for col in self.feature_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Features missing from input dataset: {missing}")

        # Validate feature types are numeric
        for col in self.feature_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Feature column '{col}' contains non-numeric data types.")

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts the selected feature subset from the input DataFrame.

        Args:
            df: Customer features DataFrame.

        Returns:
            pd.DataFrame: DataFrame containing only selected features.
        """
        # Ensure fit has validated column presence
        missing = [col for col in self.feature_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Features missing from input dataset: {missing}")

        for col in self.feature_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Feature column '{col}' contains non-numeric data types.")

        return df[self.feature_columns].copy()

    def fit_transform(self, df: pd.DataFrame, y: Optional[Any] = None) -> pd.DataFrame:
        """Fits to data, then transforms it.

        Args:
            df: Customer features DataFrame.
            y: Ignored target labels.

        Returns:
            pd.DataFrame: Transformed features DataFrame.
        """
        return self.fit(df, y).transform(df)

    def select(self, df: pd.DataFrame) -> pd.DataFrame:
        """Syntactic sugar wrapper around transform to align with business services.

        Args:
            df: Customer features DataFrame.

        Returns:
            pd.DataFrame: Selected features DataFrame.
        """
        return self.transform(df)
