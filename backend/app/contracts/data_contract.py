"""Data contract validator to verify that a DataFrame satisfies the canonical schema."""

import pandas as pd
from app.config import CANONICAL_COLUMNS
from app.utils.exceptions import InvalidSchemaError, MissingColumnError

class DataContractValidator:
    """Verifies that the preprocessed DataFrame meets all schema, type, and nullability constraints.

    Can be reused by downstream Feature Engineering, Rule Engine, and Risk Engine modules.
    """

    @staticmethod
    def validate(df: pd.DataFrame) -> None:
        """Verifies schema constraints on the provided DataFrame.

        Args:
            df: DataFrame to validate.

        Raises:
            MissingColumnError: If a required canonical column is missing.
            InvalidSchemaError: If type, uniqueness, or nullability requirements fail.
        """
        # 1. Verify that there are no duplicate column names
        if df.columns.duplicated().any():
            duplicate_cols = df.columns[df.columns.duplicated()].unique().tolist()
            raise InvalidSchemaError(f"Schema contract failed: Duplicate columns found: {duplicate_cols}")

        # 2. Verify all required columns exist
        missing_cols = [col for col in CANONICAL_COLUMNS if col not in df.columns]
        if missing_cols:
            raise MissingColumnError(f"Schema contract failed: Required columns missing: {missing_cols}")

        # 3. Verify nullability constraints on critical keys
        critical_cols = ["transaction_id", "customer_id", "sender_account", "receiver_account", "timestamp", "amount"]
        for col in critical_cols:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                raise InvalidSchemaError(
                    f"Schema contract failed: Column '{col}' contains {null_count} nulls. Nulls are not allowed in key columns."
                )

        # 4. Verify data types
        # Check datetime
        if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
            raise InvalidSchemaError(
                f"Schema contract failed: 'timestamp' must be datetime64, got {df['timestamp'].dtype}"
            )

        # Check float amount
        if not pd.api.types.is_float_dtype(df["amount"]):
            raise InvalidSchemaError(
                f"Schema contract failed: 'amount' must be float-type, got {df['amount'].dtype}"
            )

        # Check string ID fields
        id_fields = ["transaction_id", "customer_id", "sender_account", "receiver_account"]
        for col in id_fields:
            if not (pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object):
                raise InvalidSchemaError(
                    f"Schema contract failed: ID column '{col}' must be string-type, got {df[col].dtype}"
                )

        # Check categorical fields
        category_fields = ["country", "currency", "transaction_type"]
        for col in category_fields:
            if not isinstance(df[col].dtype, pd.CategoricalDtype):
                raise InvalidSchemaError(
                    f"Schema contract failed: Column '{col}' must be category-type, got {df[col].dtype}"
                )
