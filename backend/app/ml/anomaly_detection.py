"""Isolation Forest Anomaly Detection service inheriting from Base Detector.

Integrates ModelValidator checks, FeatureSchema definitions, and ModelMetadata storage.
"""

import os
import time
from typing import Any, Dict, List, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.config import ml_config
from app.ml.base_detector import AnomalyDetector
from app.ml.confidence_calculator import ConfidenceCalculator
from app.ml.exceptions import ModelPersistenceException, PredictionException
from app.ml.feature_schema import FeatureSchema
from app.ml.feature_selector import FeatureSelector
from app.ml.model_registry import ModelRegistry
from app.ml.model_validator import ModelValidator
from app.models.analysis_result import AnalysisResult
from app.models.analysis_source import AnalysisSource
from app.models.model_metadata import ModelMetadata
from app.utils.logger import get_logger

logger = get_logger(__name__)

class AnomalyDetection(AnomalyDetector):
    """Executes scikit-learn Isolation Forest model checks, implementing base AnomalyDetector."""

    def __init__(
        self,
        feature_selector: Optional[FeatureSelector] = None,
        config: Optional[Any] = None,
        model_registry: Optional[ModelRegistry] = None,
        confidence_calculator: Optional[ConfidenceCalculator] = None
    ):
        """Initializes AnomalyDetection with dependency injected services.

        Args:
            feature_selector: Selector to extract numeric behavioural columns.
            config: Configuration module override.
            model_registry: Central registry to publish or pull model states.
            confidence_calculator: Calculator to compute model prediction confidences.
        """
        self.config = config or ml_config
        self.feature_selector = feature_selector or FeatureSelector(self.config.FEATURE_COLUMNS)
        self.model_registry = model_registry or ModelRegistry()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()
        
        self.is_trained: bool = False
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: List[str] = self.feature_selector.feature_columns
        self.metadata: Optional[ModelMetadata] = None
        
        # Build simple FeatureSchema definition for column checks
        self.feature_schema = FeatureSchema(
            feature_names=self.feature_columns,
            data_types={col: "numeric" for col in self.feature_columns}
        )
        
        logger.info("Isolation Forest Detector Initialized")

    def fit(self, customer_features: pd.DataFrame) -> None:
        """Trains the StandardScaler and Isolation Forest model on numeric features.

        Args:
            customer_features: Customer features DataFrame.
        """
        logger.info("Model Training Started")
        
        # Select and validate schema features
        self.feature_selector.fit(customer_features)
        prepared = self.feature_selector.transform(customer_features)
        
        # Validate using simple FeatureSchema
        self.feature_schema.validate(prepared)
        logger.info(f"Features Selected: {self.feature_columns}")

        # Scale features
        self.scaler = StandardScaler()
        scaled = self.scaler.fit_transform(prepared)
        logger.info("Features Scaled")

        # Initialize and fit Isolation Forest
        self.model = IsolationForest(
            n_estimators=self.config.N_ESTIMATORS,
            contamination=self.config.CONTAMINATION,
            max_samples=self.config.MAX_SAMPLES,
            max_features=self.config.MAX_FEATURES,
            bootstrap=self.config.BOOTSTRAP,
            random_state=self.config.RANDOM_STATE,
            n_jobs=self.config.N_JOBS
        )
        self.model.fit(scaled)
        
        # Construct lightweight ModelMetadata
        self.metadata = ModelMetadata(
            model_name="IsolationForest",
            version="1.0",
            trained_at=time.time(),
            feature_names=self.feature_columns,
            random_state=self.config.RANDOM_STATE
        )
        
        self.is_trained = True
        logger.info("Model Training Complete")

    def predict(self, customer_features: pd.DataFrame) -> List[AnalysisResult]:
        """Performs stateless inference to identify anomalous customers, using validator checks.

        Args:
            customer_features: Customer features DataFrame.

        Returns:
            List[AnalysisResult]: Compiled anomaly results.
        """
        if not self.is_trained or self.model is None or self.scaler is None:
            raise PredictionException("Cannot predict on an untrained model. Call fit() or run() first.")

        # Prepare and extract features
        prepared = self.feature_selector.transform(customer_features)
        
        # Validate columns, ordering, NaNs, Infinites and dimensions prior to predictions
        ModelValidator.validate_features(prepared, self.feature_columns)

        # Scale features
        scaled = self.scaler.transform(prepared)

        # Infer scores
        predictions = self.model.predict(scaled)  # Inliers: 1, Outliers: -1
        decision_scores = self.model.decision_function(scaled)
        score_samples = self.model.score_samples(scaled)

        # Normalize outputs to [0, 1] (where 1.0 means highly anomalous)
        anomaly_scores = np.clip((0.5 - decision_scores) / 1.0, 0.0, 1.0)
        
        # Compute confidences using injected calculator
        confidences = self.confidence_calculator.calculate(decision_scores)

        # Map to AnalysisResult dataclass
        analysis_results: List[AnalysisResult] = []
        total_anomaly_score = 0.0
        flagged_count = 0

        for i, (_, row) in enumerate(customer_features.iterrows()):
            customer_id = str(row["customer_id"])
            anomaly_score = float(anomaly_scores[i])
            confidence = float(confidences[i])
            pred_label = int(predictions[i])
            dec_score = float(decision_scores[i])
            sample_score = float(score_samples[i])

            severity = self._classify_severity(anomaly_score)
            if pred_label == -1:
                flagged_count += 1
            total_anomaly_score += anomaly_score

            metadata = {
                "model": "IsolationForest",
                "model_version": "1.0",
                "decision_function": dec_score,
                "prediction": pred_label,
                "contamination": self.config.CONTAMINATION,
                "feature_count": len(self.feature_columns),
                "score_sample": sample_score
            }

            analysis_results.append(
                AnalysisResult(
                    customer_id=customer_id,
                    severity=severity,
                    source=AnalysisSource.ISOLATION_FOREST,
                    score=anomaly_score,
                    confidence=confidence,
                    anomaly_score=anomaly_score,
                    metadata=metadata
                )
            )

        avg_score = (total_anomaly_score / len(customer_features)) if len(customer_features) > 0 else 0.0
        
        logger.info(f"Customers Processed : {len(customer_features)}")
        logger.info(f"Customers Flagged   : {flagged_count}")
        logger.info(f"Average Anomaly Score: {avg_score:.4f}")
        logger.info("Isolation Forest Completed")

        return analysis_results

    def run(self, customer_features: pd.DataFrame) -> List[AnalysisResult]:
        """Orchestrates model execution, loading saved models if present or fitting a new one.

        Args:
            customer_features: Customer features DataFrame.

        Returns:
            List[AnalysisResult]: Compiled analysis results.
        """
        # Load cached model if possible
        if not self.is_trained:
            if os.path.exists(self.config.MODEL_PATH):
                try:
                    self.load_model(self.config.MODEL_PATH)
                except Exception as e:
                    logger.warning(f"Failed to load saved model from {self.config.MODEL_PATH}: {str(e)}. Retraining...")
                    self.fit(customer_features)
                    self.save_model(self.config.MODEL_PATH)
            else:
                self.fit(customer_features)
                self.save_model(self.config.MODEL_PATH)
        
        return self.predict(customer_features)

    def save_model(self, path: str) -> None:
        """Persists scaler and model parameters to disk along with metadata.

        Args:
            path: Target file path.
        """
        if not self.is_trained:
            raise ModelPersistenceException("Cannot save an untrained model.")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            joblib.dump({
                "model": self.model,
                "scaler": self.scaler,
                "feature_columns": self.feature_columns,
                "metadata": self.metadata
            }, path)
            logger.info(f"Model saved to {path} with metadata.")
        except Exception as e:
            raise ModelPersistenceException(f"Failed to save model: {str(e)}")

    def load_model(self, path: str) -> None:
        """Restores scaler, model, and metadata parameters from disk.

        Args:
            path: Target file path.
        """
        if not os.path.exists(path):
            raise ModelPersistenceException(f"No saved model found at {path}")
        try:
            state = joblib.load(path)
            self.model = state["model"]
            self.scaler = state["scaler"]
            self.feature_columns = state.get("feature_columns", self.config.FEATURE_COLUMNS)
            self.metadata = state.get("metadata")
            self.is_trained = True
            logger.info(f"Model loaded from {path} with metadata.")
        except Exception as e:
            raise ModelPersistenceException(f"Failed to load model: {str(e)}")

    @staticmethod
    def to_dataframe(analysis_results: List[AnalysisResult]) -> pd.DataFrame:
        """Converts List of AnalysisResult models into a Pandas DataFrame representation.

        Args:
            analysis_results: List of AnalysisResult objects.

        Returns:
            pd.DataFrame: Compiled DataFrame.
        """
        rows = []
        for res in analysis_results:
            prediction = res.metadata.get("prediction", 1)
            rows.append({
                "customer_id": res.customer_id,
                "anomaly_score": res.anomaly_score,
                "confidence": res.confidence,
                "severity": res.severity,
                "prediction": prediction,
                "metadata": res.metadata
            })
        return pd.DataFrame(rows)

    def _classify_severity(self, score: float) -> str:
        """Classifies severity based on normalized scores and config thresholds."""
        thresholds = self.config.SEVERITY_THRESHOLDS
        if score >= thresholds["CRITICAL"]:
            return "CRITICAL"
        elif score >= thresholds["HIGH"]:
            return "HIGH"
        elif score >= thresholds["MEDIUM"]:
            return "MEDIUM"
        return "LOW"

# Alias for backward compatibility
IsolationForestDetector = AnomalyDetection
