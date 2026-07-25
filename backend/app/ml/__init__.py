"""Machine learning models and processing subpackage."""

from app.ml.anomaly_detection import AnomalyDetection, IsolationForestDetector
from app.ml.base_detector import AnomalyDetector
from app.ml.confidence_calculator import ConfidenceCalculator
from app.ml.exceptions import (
    MLException,
    ModelNotFoundException,
    InvalidFeatureSchemaException,
    FeatureSelectionException,
    PredictionException,
    ModelPersistenceException
)
from app.ml.feature_schema import FeatureSchema
from app.ml.feature_selector import FeatureSelector
from app.ml.model_registry import ModelRegistry
from app.ml.model_validator import ModelValidator

# Interfaces
from app.ml.interfaces.behavioral_risk_analyzer import IBehavioralRiskAnalyzer
from app.ml.interfaces.fusion_strategy import IFusionStrategy
from app.ml.interfaces.recommendation_engine import IRecommendationStrategy, IRecommendationEngine
from app.ml.interfaces.hybrid_risk_engine import IHybridRiskEngine

# Implementations
from app.ml.behavioral_risk_analyzer import BehavioralRiskAnalyzer
from app.ml.weighted_fusion_strategy import WeightedFusionStrategy
from app.ml.deterministic_recommendation_strategy import DeterministicRecommendationStrategy
from app.ml.recommendation_engine import RecommendationEngine
from app.ml.hybrid_risk_engine import HybridRiskEngine

__all__ = [
    "AnomalyDetection",
    "IsolationForestDetector",
    "AnomalyDetector",
    "ModelRegistry",
    "FeatureSelector",
    "ConfidenceCalculator",
    "MLException",
    "ModelNotFoundException",
    "InvalidFeatureSchemaException",
    "FeatureSelectionException",
    "PredictionException",
    "ModelPersistenceException",
    "FeatureSchema",
    "ModelValidator",
    
    # Interfaces
    "IBehavioralRiskAnalyzer",
    "IFusionStrategy",
    "IRecommendationStrategy",
    "IRecommendationEngine",
    "IHybridRiskEngine",
    
    # Implementations
    "BehavioralRiskAnalyzer",
    "WeightedFusionStrategy",
    "DeterministicRecommendationStrategy",
    "RecommendationEngine",
    "HybridRiskEngine"
]
