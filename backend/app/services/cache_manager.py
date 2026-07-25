"""Cache management service for serialization of preprocessed DataFrames."""

import hashlib
import os
import pickle
from typing import Optional
import pandas as pd
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Calculates dataset hashes, performs cache lookups, and saves preprocessed outputs.

    Uses fast binary pickle serialization to preserve pandas dtypes (categories/datetimes).
    """

    @staticmethod
    def calculate_file_hash(filepath: str) -> str:
        """Computes the MD5 checksum of a file.

        Args:
            filepath: Path to the target file.

        Returns:
            str: Hex digest of the MD5 checksum.
        """
        hasher = hashlib.md5()
        # Read in 64KB blocks to keep memory footprint low
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def load_cached_dataset(file_hash: str, cache_dir: str) -> Optional[pd.DataFrame]:
        """Retrieves preprocessed dataset from pickle cache if it exists.

        Args:
            file_hash: The MD5 checksum of the raw dataset.
            cache_dir: Path to the cache directory.

        Returns:
            Optional[pd.DataFrame]: Cached DataFrame or None if Cache Miss.
        """
        cache_path = os.path.join(cache_dir, f"{file_hash}.pkl")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    df = pickle.load(f)
                logger.info(f"Cache HIT: Preprocessed dataset loaded from {cache_path}")
                return df
            except Exception as e:
                logger.warning(f"Failed to load cache file {cache_path}: {str(e)}. Preprocessing will re-run.")
        else:
            logger.info("Cache MISS: No cached dataset matches this file hash.")
        return None

    @staticmethod
    def save_to_cache(df: pd.DataFrame, file_hash: str, cache_dir: str) -> None:
        """Caches preprocessed dataset to disk.

        Args:
            df: Clean preprocessed DataFrame.
            file_hash: MD5 checksum of the raw dataset.
            cache_dir: Path to the cache directory.
        """
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, f"{file_hash}.pkl")
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(df, f)
            logger.info(f"Cached preprocessed dataset to {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to write cache file {cache_path}: {str(e)}")
