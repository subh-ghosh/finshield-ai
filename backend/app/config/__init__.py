"""Config package exports defining PipelineConfig, PIPELINE_VERSION, and CANONICAL_COLUMNS."""

from dataclasses import dataclass

# Current pipeline version
PIPELINE_VERSION = "1.0.0"

# Centralized output schema data contract columns
CANONICAL_COLUMNS = [
    "transaction_id",
    "customer_id",
    "sender_account",
    "receiver_account",
    "timestamp",
    "amount",
    "currency",
    "country",
    "transaction_type"
]

@dataclass
class PipelineConfig:
    """Type-safe configuration dataclass for the preprocessing pipeline.

    Provides validation, autocomplete, and settings for all pipeline stages.
    """
    remove_duplicates: bool = True
    validate_amounts: bool = True
    save_rejected_rows: bool = True
    generate_metadata: bool = True
    generate_report: bool = True
    sort_records: bool = True
    use_cache: bool = True
    
    # System directory paths
    reports_dir: str = "reports"
    rejected_dir: str = "reports/rejected"
    cache_dir: str = ".cache"
    feature_store_dir: str = ".feature_store"

    def __post_init__(self) -> None:
        """Performs simple type validations on config fields."""
        for field_name, expected_type in [
            ("remove_duplicates", bool),
            ("validate_amounts", bool),
            ("save_rejected_rows", bool),
            ("generate_metadata", bool),
            ("generate_report", bool),
            ("sort_records", bool),
            ("use_cache", bool),
            ("reports_dir", str),
            ("rejected_dir", str),
            ("cache_dir", str),
            ("feature_store_dir", str)
        ]:
            val = getattr(self, field_name)
            if not isinstance(val, expected_type):
                raise TypeError(
                    f"Config field '{field_name}' must be of type {expected_type.__name__}, got {type(val).__name__}"
                )
