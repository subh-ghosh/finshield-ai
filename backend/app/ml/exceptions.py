"""Custom domain exceptions for the Machine Learning layer."""

class MLException(Exception):
    """Base exception class for all ML-related errors in the platform."""
    pass

class ModelNotFoundException(MLException):
    """Raised when an ML model cannot be loaded or is missing from the registry."""
    pass

class InvalidFeatureSchemaException(MLException):
    """Raised when an incoming feature matrix fails schema or type validation checks."""
    pass

class FeatureSelectionException(MLException):
    """Raised when features cannot be prepared or selected correctly by the selector."""
    pass

class PredictionException(MLException):
    """Raised when an error occurs during model forward-pass predictions."""
    pass

class ModelPersistenceException(MLException):
    """Raised when errors occur during serialization or deserialization of models."""
    pass
