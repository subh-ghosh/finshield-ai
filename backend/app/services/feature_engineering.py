"""Feature engineering service for computing customer-level behavioral and temporal features."""

import pandas as pd
import numpy as np
from app.utils.logger import get_logger
from app.services.graph_analysis import GraphAnalyzer
from app.ml.sequence_model import TransactionSequenceModel

logger = get_logger(__name__)

class FeatureEngineering:
    """Computes customer behavioral, temporal, and risk-oriented features from clean transactions.

    Structured with private methods to allow future scaling of AML features.
    """

    def __init__(self):
        self.graph_analyzer = GraphAnalyzer()
        self.sequence_model = TransactionSequenceModel()

    def run(self, clean_dataframe: pd.DataFrame) -> pd.DataFrame:
        """Runs the feature engineering pipeline from end to end.

        Args:
            clean_dataframe: Clean preprocessed transactions DataFrame.

        Returns:
            pd.DataFrame: Engineered customer feature matrix.
        """
        logger.info("Starting advanced 2026 feature engineering...")
        
        # Parse dates if timestamp exists
        if "timestamp" in clean_dataframe.columns:
            clean_dataframe["timestamp"] = pd.to_datetime(clean_dataframe["timestamp"])
            
        # 0. Run Analysis
        network_risks = self.graph_analyzer.run(clean_dataframe)
        self.sequence_model.fit(clean_dataframe)
        sequence_perplexity = self.sequence_model.score_customers(clean_dataframe)
        
        # 1. Compute basic transaction aggregations (grouped by customer)
        features_df = self._basic_aggregations(clean_dataframe)
        
        # 2. Add temporal features (ratios, windows, recency)
        features_df = self._temporal_features(clean_dataframe, features_df)
        
        # 3. Add behavioral fingerprints (velocity, diversity, smurfing, sequence perplexity)
        features_df = self._behavioral_fingerprints(clean_dataframe, features_df, network_risks, sequence_perplexity)
        
        # 4. Finalize features (sorting, re-ordering)
        features_df = self._finalize(features_df)
        
        logger.info(f"Feature engineering complete. Computed high-dimensional features for {len(features_df)} customers.")
        return features_df

    def _basic_aggregations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Groups transactions by customer and computes basic metrics."""
        agg_df = df.groupby("customer_id").agg(
            transaction_count=("transaction_id", "count"),
            total_amount=("amount", "sum"),
            average_amount=("amount", "mean"),
            maximum_amount=("amount", "max"),
            minimum_amount=("amount", "min")
        ).reset_index()
        return agg_df

    def _temporal_features(self, raw_df: pd.DataFrame, agg_df: pd.DataFrame) -> pd.DataFrame:
        """Appends temporal placeholders and calculations to the feature matrix."""
        df = agg_df.copy()
        
        if "timestamp" not in raw_df.columns:
            df["night_transaction_ratio"] = 0.0
            df["weekend_transaction_ratio"] = 0.0
            df["rolling_amount_24h"] = 0.0
            df["rolling_count_24h"] = 0
            df["days_since_last_transaction"] = 0.0
            return df
            
        # Time-based features
        raw_df["is_night"] = raw_df["timestamp"].dt.hour.isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)
        raw_df["is_weekend"] = raw_df["timestamp"].dt.dayofweek.isin([5, 6]).astype(int)
        
        time_agg = raw_df.groupby("customer_id").agg(
            night_count=("is_night", "sum"),
            weekend_count=("is_weekend", "sum"),
            last_txn_date=("timestamp", "max")
        ).reset_index()
        
        df = df.merge(time_agg, on="customer_id", how="left")
        
        df["night_transaction_ratio"] = df["night_count"] / df["transaction_count"]
        df["weekend_transaction_ratio"] = df["weekend_count"] / df["transaction_count"]
        
        current_time = raw_df["timestamp"].max()
        df["days_since_last_transaction"] = (current_time - df["last_txn_date"]).dt.total_seconds() / 86400.0
        
        df = df.drop(columns=["night_count", "weekend_count", "last_txn_date"])
        
        df["rolling_amount_24h"] = df["average_amount"] * (df["transaction_count"] / max(1, df["days_since_last_transaction"].mean()))
        df["rolling_count_24h"] = df["transaction_count"] / max(1, df["days_since_last_transaction"].mean())
        
        return df

    def _behavioral_fingerprints(self, raw_df: pd.DataFrame, agg_df: pd.DataFrame, network_risks: dict, sequence_perplexity: dict) -> pd.DataFrame:
        """Appends behavioral fingerprints (velocity, diversity, structuring) to the feature matrix."""
        df = agg_df.copy()
        
        # Map network risk
        df["network_risk_score"] = df["customer_id"].map(lambda x: network_risks.get(str(x), 0.0))
        # Add sequence perplexity
        df["sequence_perplexity"] = df["customer_id"].map(lambda x: sequence_perplexity.get(x, 0.0))
        
        # Structuring score (count of transactions between $9k and $10k)
        raw_df["is_structuring"] = ((raw_df["amount"] >= 9000) & (raw_df["amount"] < 10000)).astype(int)
        struct_agg = raw_df.groupby("customer_id").agg(structuring_count=("is_structuring", "sum")).reset_index()
        df = df.merge(struct_agg, on="customer_id", how="left")
        df["structuring_score"] = df["structuring_count"] / df["transaction_count"]
        
        # Velocity score (Z-Score approximation of frequency)
        if "days_since_last_transaction" in df.columns:
            avg_days = df["days_since_last_transaction"].mean()
            std_days = df["days_since_last_transaction"].std()
            if std_days > 0:
                # Lower days since last transaction = higher velocity
                df["velocity_score"] = (avg_days - df["days_since_last_transaction"]) / std_days
            else:
                df["velocity_score"] = 0.0
        else:
            df["velocity_score"] = 0.0
            
        # Fill missing values
        df["velocity_score"] = df["velocity_score"].fillna(0.0)
            
        df["smurfing_score"] = df["structuring_score"] * df["velocity_score"]
        
        # Diversity
        receiver_col = "recipient_id" if "recipient_id" in raw_df.columns else "receiver_account_id"
        if receiver_col in raw_df.columns:
            div_agg = raw_df.groupby("customer_id")[receiver_col].nunique().reset_index()
            div_agg.columns = ["customer_id", "unique_recipients"]
            df = df.merge(div_agg, on="customer_id", how="left")
            df["recipient_diversity"] = df["unique_recipients"] / df["transaction_count"]
            df = df.drop(columns=["unique_recipients"])
        else:
            df["recipient_diversity"] = 0.0
            
        df["sender_diversity"] = 0.0
        df["cash_in_ratio"] = 0.5
        df["cash_out_ratio"] = 0.5
        
        raw_df["is_round"] = (raw_df["amount"] % 100 == 0).astype(int)
        round_agg = raw_df.groupby("customer_id").agg(round_count=("is_round", "sum")).reset_index()
        df = df.merge(round_agg, on="customer_id", how="left")
        df["round_amount_ratio"] = df["round_count"] / df["transaction_count"]
        
        df["account_age"] = df["days_since_last_transaction"] * 2.0
        df["risk_score_placeholder"] = df["network_risk_score"]
        
        # Cleanup
        if "structuring_count" in df.columns:
            df = df.drop(columns=["structuring_count"])
        if "round_count" in df.columns:
            df = df.drop(columns=["round_count"])
            
        # Fill NaN
        df = df.fillna(0.0)
        
        return df

    def _finalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reorders columns and sorts features by customer ID."""
        df = df.copy()
        df = df.sort_values(by="customer_id").reset_index(drop=True)
        
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
            "network_risk_score"
        ]
        
        cols = [col for col in expected_order if col in df.columns] + [col for col in df.columns if col not in expected_order]
        return df[cols]
