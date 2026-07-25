"""Abstract base class interface for all Anomaly Detection models."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List
from app.models.analysis_result import AnalysisResult

class AnomalyDetector(ABC):
    """Abstract interface defining the standardized lifecycle for AML anomaly detectors."""

    @abstractmethod
    def fit(self, customer_features: pd.DataFrame) -> None:
        """Trains the model and any internal scalers on the customer features matrix.

        Args:
            customer_features: Customer features DataFrame.
        """
        pass

    @abstractmethod
    def predict(self, customer_features: pd.DataFrame) -> List[AnalysisResult]:
        """Runs stateless outlier predictions on the input features.

        Args:
            customer_features: Customer features DataFrame.

        Returns:
            List[AnalysisResult]: List of compiled outlier alert dataclasses.
        """
        pass

    @abstractmethod
    def run(self, customer_features: pd.DataFrame) -> List[AnalysisResult]:
        """Orchestrates loading, fitting, and predicting flow.

        Args:
            customer_features: Customer features DataFrame.

        Returns:
            List[AnalysisResult]: List of compiled outlier alert dataclasses.
        """
        pass

    @abstractmethod
    def save_model(self, path: str) -> None:
        """Serializes model parameters and configuration state to disk.

        Args:
            path: Target serialization filepath.
        """
        pass

    @abstractmethod
    def load_model(self, path: str) -> None:
        """Deserializes model parameters and configuration state from disk.

        Args:
            path: Target deserialization filepath.
        """
        pass
