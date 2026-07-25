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
