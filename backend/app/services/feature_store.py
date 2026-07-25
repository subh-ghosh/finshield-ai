"""Local Feature Store service for persisting and managing engineered customer features."""

import os
import pickle
from typing import Optional
import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

class FeatureStore:
    """Manages local storage of engineered customer-level features.

    Features are serialized to a local binary pickle file.
    """

    def __init__(self, store_dir: str = ".feature_store"):
        """Initializes the Feature Store directory.

        Args:
            store_dir: Path to directory for feature storage.
        """
        self.store_dir = store_dir
        os.makedirs(self.store_dir, exist_ok=True)
        self.path = os.path.join(self.store_dir, "customer_features.pkl")

    def save(self, df: pd.DataFrame) -> None:
        """Saves the customer features DataFrame to the store.

        Args:
            df: The customer feature matrix.
        """
        try:
            with open(self.path, "wb") as f:
                pickle.dump(df, f)
            logger.info(f"Feature Store: Saved customer features to {self.path}")
        except Exception as e:
            logger.error(f"Feature Store: Failed to save customer features: {str(e)}")

    def load(self) -> Optional[pd.DataFrame]:
        """Loads the customer features DataFrame from the store.

        Returns:
            Optional[pd.DataFrame]: The customer features DataFrame or None.
        """
        if os.path.exists(self.path):
            try:
                with open(self.path, "rb") as f:
                    df = pickle.load(f)
                logger.info(f"Feature Store: Loaded customer features from {self.path}")
                return df
            except Exception as e:
                logger.error(f"Feature Store: Failed to load customer features: {str(e)}")
        else:
            logger.info("Feature Store: No customer features found.")
        return None

    def update(self, df: pd.DataFrame) -> None:
        """Updates the customer features dataset.

        Args:
            df: The updated customer feature matrix.
        """
        self.save(df)

    def clear(self) -> None:
        """Removes the customer features pickle file from disk."""
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
                logger.info("Feature Store: Cleared customer features store file.")
            except Exception as e:
                logger.error(f"Feature Store: Failed to clear customer features: {str(e)}")
