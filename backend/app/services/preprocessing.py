"""Data preprocessing service for AML transaction datasets."""

from dataclasses import dataclass, field
import json
import os
import re
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from app.config import CANONICAL_COLUMNS, PIPELINE_VERSION
from app.contracts.data_contract import DataContractValidator
from app.utils.exceptions import InvalidSchemaError, MissingColumnError
from app.utils.logger import get_logger
from app.utils.schema_mapper import SchemaMapper

logger = get_logger(__name__)

@dataclass
class PreprocessingReport:
    """Statistics, metrics, and logs gathered during the preprocessing execution."""
    total_rows: int
    clean_rows: int
    missing_percentage: float
    duplicate_percentage: float
    invalid_percentage: float
    null_columns: List[str]
    completeness_score: float
    execution_time: float
    columns_normalized: List[str]
    schema_mappings: Dict[str, str]
    warnings: List[str]
    data_quality_score: float


class AMLPreprocessor:
    """Executes data cleaning, schema validation, and profiling for AML transaction data.

    Preserves audit trails of rejected records and validates schemas against
    centralized data contracts.
    """

    def __init__(self):
        """Initializes preprocessor state."""
        self.df: Optional[pd.DataFrame] = None
        self.raw_df: Optional[pd.DataFrame] = None
        self.clean_df: Optional[pd.DataFrame] = None
        
        # Rejected rows dataframes for audits
        self.duplicate_df: Optional[pd.DataFrame] = None
        self.invalid_df: Optional[pd.DataFrame] = None
        self.missing_df: Optional[pd.DataFrame] = None
        
        # Ingestion metrics
        self.rows_loaded: int = 0
        self.columns_normalized: List[str] = []
        self.schema_mappings: Dict[str, str] = {}
        self.null_columns: List[str] = []
        self.warnings: List[str] = []
        self.data_quality_score: float = 100.0

    def load_data(self, filepath: str) -> pd.DataFrame:
        """Loads dataset from file using the DatasetLoader.

        Args:
            filepath: Path to the CSV file.

        Returns:
            pd.DataFrame: Loaded raw DataFrame.
        """
        from app.services.dataset_loader import DatasetLoader
        
        self.raw_df = DatasetLoader.load_transaction_dataset(filepath)
        self.df = self.raw_df.copy()
        self.rows_loaded = len(self.df)
        
        # Compute null columns and metrics from raw data
        self.null_columns = [col for col in self.raw_df.columns if self.raw_df[col].isnull().any()]
        
        # Check if accounts.csv was missing from dataset load
        dir_path = os.path.dirname(os.path.abspath(filepath))
        accounts_path = os.path.join(dir_path, "accounts.csv")
        if not os.path.exists(accounts_path):
            self.warnings.append("Warning: accounts.csv not found. customer_id mapping will rely on raw dataset.")
            
        return self.df

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts every column name of the DataFrame to snake_case.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with normalized column names.
        """
        df = df.copy()
        normalized_cols = []
        for col in df.columns:
            # Handle PascalCase/camelCase splits (insert underscore)
            name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", col)
            name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
            # Replace non-alphanumeric separators with underscores
            name = re.sub(r"[\s\-.]+", "_", name)
            # Strip outer underscores and convert to lowercase
            normalized = re.sub(r"_+", "_", name).lower().strip("_")
            normalized_cols.append(normalized)
            
        df.columns = normalized_cols
        self.columns_normalized = normalized_cols
        return df

    def map_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Applies intelligent alias matching to rename raw columns to canonical fields.

        Args:
            df: Column-normalized DataFrame.

        Returns:
            pd.DataFrame: DataFrame with columns renamed to canonical contract names.
        """
        df = df.copy()
        self.schema_mappings = SchemaMapper.get_mappings(df.columns.tolist())
        df = df.rename(columns=self.schema_mappings)

        # Impute missing categorical canonical columns to satisfy Data Contract
        categorical_fallbacks = {
            "currency": "UNKNOWN",
            "country": "UNKNOWN",
            "transaction_type": "UNKNOWN"
        }
        for col, default_val in categorical_fallbacks.items():
            if col not in df.columns:
                df[col] = default_val
                logger.info(f"Canonical column '{col}' missing from raw dataset. Imputed with '{default_val}'.")
                self.warnings.append(f"Warning: Canonical column '{col}' was missing and imputed with '{default_val}'.")

        return df

    def validate_schema(self, df: pd.DataFrame) -> None:
        """Ensures that required columns exist in the DataFrame post-mapping.

        Args:
            df: Renovated DataFrame.

        Raises:
            MissingColumnError: If a required canonical column is missing.
        """
        # Critical structural validation
        missing_cols = [col for col in ["transaction_id", "sender_account", "receiver_account", "timestamp", "amount", "customer_id"] if col not in df.columns]
        if missing_cols:
            raise MissingColumnError(f"Required column(s) missing from schema: {missing_cols}")

    def convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Converts columns of the DataFrame to canonical pandas dtypes.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with standardized dtypes.
        """
        df = df.copy()

        # 1. Convert Timestamp to datetime64
        if "timestamp" in df.columns:
            if pd.api.types.is_numeric_dtype(df["timestamp"]):
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", errors="coerce")
            else:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # 2. Convert Amount to float32
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").astype(np.float32)

        # 3. Convert ID columns to clean string fields
        id_cols = ["transaction_id", "customer_id", "sender_account", "receiver_account", "account_id"]
        for col in id_cols:
            if col in df.columns:
                # Optimized vectorized ID cast preserving NaNs as actual nulls
                if pd.api.types.is_numeric_dtype(df[col]):
                    non_null = df[col].dropna()
                    if len(non_null) > 0 and (non_null % 1 == 0).all():
                        df[col] = df[col].astype("Int64").astype(str).replace("<NA>", np.nan)
                        continue
                df[col] = df[col].astype(str).replace(["nan", "None", "<NA>"], np.nan)

        # 4. Convert category columns
        cat_cols = ["country", "currency", "transaction_type"]
        for col in cat_cols:
            if col in df.columns:
                df[col] = df[col].astype("category")

        return df

    def clean_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts rows with missing key columns to an audit dataframe and handles categories.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: DataFrame with missing values resolved.
        """
        df = df.copy()
        
        # Key fields that cannot contain nulls
        critical_cols = ["transaction_id", "customer_id", "sender_account", "receiver_account", "timestamp", "amount"]
        
        # Vectorized check for nulls
        null_mask = df[critical_cols].isnull().any(axis=1)
        
        # Check for empty string IDs
        empty_str_mask = pd.Series(False, index=df.index)
        for col in ["transaction_id", "customer_id", "sender_account", "receiver_account"]:
            if col in df.columns:
                empty_str_mask = empty_str_mask | (df[col].astype(str).str.strip() == "")
                
        missing_mask = null_mask | empty_str_mask
        
        # Segment out missing rows for auditing
        self.missing_df = df[missing_mask].copy()
        clean_df = df[~missing_mask].copy()

        # Fallback category values
        if "country" in clean_df.columns:
            clean_df["country"] = clean_df["country"].cat.add_categories("UNKNOWN").fillna("UNKNOWN")
        if "transaction_type" in clean_df.columns:
            clean_df["transaction_type"] = clean_df["transaction_type"].cat.add_categories("UNKNOWN").fillna("UNKNOWN")

        return clean_df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Deduplicates rows by transaction_id, exporting duplicates to an audit dataframe.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: Deduplicated DataFrame.
        """
        df = df.copy()
        
        duplicate_mask = df.duplicated(subset=["transaction_id"], keep="first")
        
        self.duplicate_df = df[duplicate_mask].copy()
        clean_df = df[~duplicate_mask].copy()
        
        return clean_df

    def validate_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Checks for impossible transaction amounts or invalid timestamps.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: Validated DataFrame.
        """
        df = df.copy()

        # Impossible values: amount <= 0, NaN amount, infinite amount, or missing timestamp
        invalid_amount = (df["amount"] <= 0) | df["amount"].isnull() | ~np.isfinite(df["amount"])
        invalid_time = df["timestamp"].isnull()
        
        invalid_mask = invalid_amount | invalid_time
        
        self.invalid_df = df[invalid_mask].copy()
        clean_df = df[~invalid_mask].copy()
        
        return clean_df

    def sort_by_timestamp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sorts the dataframe by customer_id and timestamp.

        Args:
            df: Input DataFrame.

        Returns:
            pd.DataFrame: Sorted DataFrame.
        """
        df = df.copy()
        df = df.sort_values(by=["customer_id", "timestamp"], ascending=[True, True])
        return df.reset_index(drop=True)

    def generate_report(self, execution_time: float) -> PreprocessingReport:
        """Compiles metric counts, percentage rates, and warning states.

        Args:
            execution_time: Preprocessing stage runtime (seconds).

        Returns:
            PreprocessingReport: Summary report instance.
        """
        total = self.rows_loaded
        clean = len(self.clean_df) if self.clean_df is not None else 0
        missing = len(self.missing_df) if self.missing_df is not None else 0
        dup = len(self.duplicate_df) if self.duplicate_df is not None else 0
        invalid = len(self.invalid_df) if self.invalid_df is not None else 0

        missing_pct = (missing / total * 100.0) if total > 0 else 0.0
        dup_pct = (dup / total * 100.0) if total > 0 else 0.0
        invalid_pct = (invalid / total * 100.0) if total > 0 else 0.0

        # Calculate completeness score of the raw dataset
        total_cells = self.raw_df.size if self.raw_df is not None else 0
        total_nulls = self.raw_df.isnull().sum().sum() if self.raw_df is not None else 0
        completeness = ((total_cells - total_nulls) / total_cells * 100.0) if total_cells > 0 else 100.0

        # Calculate Data Quality Score
        total_rejected = missing + dup + invalid
        self.data_quality_score = max(0.0, 100.0 * (1.0 - (total_rejected / total)) if total > 0 else 100.0)

        # Collect warning triggers
        if self.data_quality_score < 90.0:
            self.warnings.append(f"Warning: Low data quality score ({self.data_quality_score:.2f}%). Check raw dataset.")
        if dup > 0:
            self.warnings.append(f"Warning: Found {dup} duplicate transaction IDs.")
        if missing > 0:
            self.warnings.append(f"Warning: Found {missing} rows with missing key fields.")
        if invalid > 0:
            self.warnings.append(f"Warning: Found {invalid} rows with invalid amounts or timestamps.")

        return PreprocessingReport(
            total_rows=total,
            clean_rows=clean,
            missing_percentage=round(missing_pct, 4),
            duplicate_percentage=round(dup_pct, 4),
            invalid_percentage=round(invalid_pct, 4),
            null_columns=self.null_columns,
            completeness_score=round(completeness, 2),
            execution_time=round(execution_time, 4),
            columns_normalized=self.columns_normalized,
            schema_mappings=self.schema_mappings,
            warnings=list(set(self.warnings)),
            data_quality_score=round(self.data_quality_score, 2)
        )

    def save_clean_dataset(self, path: str) -> None:
        """Persists the preprocessed clean dataset as a CSV.

        Args:
            path: Target file path.
        """
        if self.clean_df is None:
            raise InvalidSchemaError("No clean dataset has been preprocessed yet.")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.clean_df.to_csv(path, index=False)
        logger.info(f"Clean dataset persisted to: {path}")

    def save_metadata(self, path: str, execution_time: float) -> None:
        """Generates and writes metadata.json file.

        Args:
            path: Target JSON file path.
            execution_time: Runtime of the preprocessor.
        """
        metadata = {
            "dataset": "IBM AMLSim",
            "pipeline_version": PIPELINE_VERSION,
            "processed_at": pd.Timestamp.now().isoformat(),
            "rows": self.rows_loaded,
            "columns": len(self.clean_df.columns) if self.clean_df is not None else 0,
            "duplicates_removed": len(self.duplicate_df) if self.duplicate_df is not None else 0,
            "runtime_seconds": round(execution_time, 4),
            "data_quality_score": round(self.data_quality_score, 2)
        }
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"Metadata file written to: {path}")

    def generate_profile(self, path: str) -> None:
        """Generates a dataset profile JSON and saves it.

        Args:
            path: Target path for the dataset profile.
        """
        if self.clean_df is None:
            raise InvalidSchemaError("No clean dataset has been preprocessed yet.")

        df = self.clean_df
        
        # Calculate categories cardinality
        cardinality = {}
        for col in df.columns:
            if isinstance(df[col].dtype, pd.CategoricalDtype):
                cardinality[col] = int(df[col].nunique())

        profile = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "memory_usage": int(df.memory_usage(deep=True).sum()),
            "column_types": {col: str(df[col].dtype) for col in df.columns},
            "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
            "duplicate_count": int(df.duplicated().sum()),
            "category_cardinality": cardinality,
            "date_range": {
                "min": str(df["timestamp"].min()),
                "max": str(df["timestamp"].max())
            } if "timestamp" in df.columns else {},
            "amount_statistics": {
                "min": float(df["amount"].min()),
                "max": float(df["amount"].max()),
                "mean": float(df["amount"].mean()),
                "median": float(df["amount"].median())
            } if "amount" in df.columns else {}
        }

        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w") as f:
            json.dump(profile, f, indent=4)
        logger.info(f"Dataset profile saved to: {path}")

    def preprocess(self, filepath: str) -> pd.DataFrame:
        """Fallback method to run full pipeline on preprocessor itself."""
        self.load_data(filepath)
        df = self.normalize_column_names(self.df)
        df = self.map_schema(df)
        self.validate_schema(df)
        df = self.convert_dtypes(df)
        df = self.clean_missing_values(df)
        df = self.remove_duplicates(df)
        df = self.validate_amounts(df)
        df = self.sort_by_timestamp(df)
        self.clean_df = df
        return df
