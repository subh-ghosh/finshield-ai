"""Feature engineering service for computing customer-level behavioral and temporal features."""

import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureEngineering:
    """Computes customer behavioral, temporal, and risk-oriented features from clean transactions.

    Structured with private methods to allow future scaling of AML features.
    """

    def run(self, clean_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Runs the feature engineering pipeline from end to end.

        Args:
            clean_dataframe: Clean preprocessed transactions DataFrame.

        Returns:
            pd.DataFrame: Engineered customer feature matrix.
        """
        logger.info("Starting feature engineering...")
        
        # 1. Compute basic transaction aggregations (grouped by customer)
        features_df = self._basic_aggregations(clean_dataframe)
        
        # 2. Add temporal features (ratios, windows, recency)
        features_df = self._temporal_features(features_df)
        
        # 3. Add behavioral placeholders (velocity, diversity, smurfing)
        features_df = self._behavioral_placeholders(features_df)
        
        # 4. Finalize features (sorting, re-ordering)
        features_df = self._finalize(features_df)
        
        logger.info(f"Feature engineering complete. Computed features for {len(features_df)} customers.")
        return features_df

    def _basic_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Groups transactions by customer and computes basic metrics."""
        # Vectorized groupby agg
        agg_df = df.groupby("customer_id").agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            average_amount=("amount", "mean"),
            maximum_amount=("amount", "max"),
            minimum_amount=("amount", "min")
        ).reset_index()
        return agg_df

    def _temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Appends temporal placeholders and calculations to the feature matrix."""
        df = df.copy()
        
        # Placeholder values for temporal features (to be calculated with actual dates later)
        df["night_transaction_ratio"] = 0.0
        df["weekend_transaction_ratio"] = 0.0
        df["rolling_amount_24h"] = 0.0
        df["rolling_count_24h"] = 0
        df["days_since_last_transaction"] = 0.0
        
        return df

    def _behavioral_placeholders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Appends behavioral placeholders to the feature matrix."""
        df = df.copy()
        
        # Extensible behavioral features for Rule Engine & Anomaly Models
        df["velocity_score"] = 0.0
        df["structuring_score"] = 0.0
        df["smurfing_score"] = 0.0
        df["recipient_diversity"] = 0.0
        df["sender_diversity"] = 0.0
        df["cash_in_ratio"] = 0.0
        df["cash_out_ratio"] = 0.0
        df["round_amount_ratio"] = 0.0
        df["account_age"] = 0.0
        df["risk_score_placeholder"] = 0.0
        
        return df

    def _finalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorders columns and sorts features by customer ID."""
        df = df.copy()
        df = df.sort_values(by="customer_id").reset_index(drop=True)
        
        # Ensure column ordering is clean
        expected_order = [
            "customer_id",
            "transaction_count",
            "total_amount",
            "average_amount",
            "maximum_amount",
            "minimum_amount",
            "velocity_score",
            "structuring_score",
            "smurfing_score",
            "recipient_diversity",
            "sender_diversity",
            "cash_in_ratio",
            "cash_out_ratio",
            "night_transaction_ratio",
            "weekend_transaction_ratio",
            "round_amount_ratio",
            "rolling_amount_24h",
            "rolling_count_24h",
            "days_since_last_transaction",
            "account_age",
            "risk_score_placeholder"
        ]
        
        # Put columns in the expected order, keeping any extra columns at the end
        cols = [col for col in expected_order if col in df.columns] + [col for col in df.columns if col not in expected_order]
        return df[cols]
