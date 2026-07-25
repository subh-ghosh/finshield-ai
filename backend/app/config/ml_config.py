"""Centralized configuration module for all Machine Learning layer hyperparameters and settings."""

# Isolation Forest hyperparameters
N_ESTIMATORS: int = 100
CONTAMINATION: float = 0.02
MAX_SAMPLES: str = "auto"
MAX_FEATURES: float = 1.0
BOOTSTRAP: bool = False
RANDOM_STATE: int = 42
N_JOBS: int = -1

# Feature scaling configuration options
SCALER_TYPE: str = "standard"  # Support "standard" scaling (via StandardScaler)

# Model serialization paths
MODEL_PATH: str = ".cache/models/isolation_forest.pkl"
MODEL_SAVE_DIR: str = ".cache/models"

# Features selected for anomaly detection (numerical, behavioral metrics only)
FEATURE_COLUMNS: list = [
    "transaction_count",
    "total_amount",
    "average_amount",
    "maximum_amount",
    "velocity_score",
    "structuring_score",
    "recipient_diversity",
    "sender_diversity",
    "cash_out_ratio",
    "night_transaction_ratio",
    "weekend_transaction_ratio",
    "rolling_amount_24h",
    "rolling_count_24h",
    "days_since_last_transaction"
]

# Anomaly score severity classification thresholds
SEVERITY_THRESHOLDS: dict = {
    "LOW": 0.3,
    "MEDIUM": 0.45,
    "HIGH": 0.6,
    "CRITICAL": 0.75
}

# Hybrid Risk Engine configuration options
HYBRID_WEIGHTS: dict = {
    "rule_engine": 0.60,
    "isolation_forest": 0.30,
    "behavioural": 0.10
}

HYBRID_SEVERITY_THRESHOLDS: dict = {
    "LOW": 0.25,
    "MEDIUM": 0.35,
    "HIGH": 0.50,
    "CRITICAL": 0.75
}

# Configurable recommendation rules matching scores to actions
HYBRID_RECOMMENDATION_RULES: list = [
    {"min_score": 0.75, "recommendation": "Immediate Investigation"},
    {"min_score": 0.50, "recommendation": "File SAR Recommendation"},
    {"min_score": 0.35, "recommendation": "Escalate Investigation"},
    {"min_score": 0.25, "recommendation": "Manual Review"},
    {"min_score": 0.00, "recommendation": "Continue Monitoring"}
]

# Configurable behavioural indicators and their bounds/weights
BEHAVIORAL_INDICATORS: dict = {
    "velocity_score": {"max": 10.0, "weight": 0.25},
    "structuring_score": {"max": 10.0, "weight": 0.25},
    "cash_out_ratio": {"max": 1.0, "weight": 0.20},
    "recipient_diversity": {"max": 15.0, "weight": 0.15},
    "sender_diversity": {"max": 5.0, "weight": 0.15}
}

