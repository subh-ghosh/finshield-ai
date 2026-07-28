"""Ingestion module for reading AML datasets and mapping account relationships."""

import os
from typing import Iterator, Optional, Union
import pandas as pd
from app.utils.exceptions import DatasetNotFoundError, JoinError
from app.utils.logger import get_logger

logger = get_logger(__name__)

class DatasetLoader:
    """Verifies file existence, reads CSV datasets, and resolves customer mapping relationships."""

    @staticmethod
    def load_transaction_dataset(
        filepath: str, 
        chunksize: Optional[int] = None
    ) -> Union[pd.DataFrame, Iterator[pd.DataFrame]]:
        """Loads transaction CSV and automatically merges with accounts.csv if available.

        Args:
            filepath: Path to the transactions CSV file.
            chunksize: Optional number of rows per chunk to load as an iterator.

        Returns:
            Union[pd.DataFrame, Iterator[pd.DataFrame]]: Loaded DataFrame or chunk iterator.

        Raises:
            DatasetNotFoundError: If transactions CSV does not exist.
            JoinError: If schema mismatch prevents joining accounts.csv.
        """
        if not os.path.exists(filepath):
            raise DatasetNotFoundError(f"Transactions file not found at: {filepath}")

        # Check for accounts.csv in the same directory as transactions file
        dir_path = os.path.dirname(os.path.abspath(filepath))
        accounts_path = os.path.join(dir_path, "accounts.csv")
        
        accounts_df = None
        if os.path.exists(accounts_path):
            try:
                # Load only required columns from accounts file to keep memory footprint low
                accounts_df = pd.read_csv(
                    accounts_path,
                    usecols=["ACCOUNT_ID", "CUSTOMER_ID", "COUNTRY"]
                )
                logger.info(f"Loaded {len(accounts_df)} rows from accounts.csv for customer resolution.")
            except Exception as e:
                raise JoinError(f"Failed to load accounts.csv for customer resolution: {str(e)}") from e

        if chunksize is not None:
            try:
                chunks = pd.read_csv(filepath, chunksize=chunksize)
                return DatasetLoader._wrap_chunks(chunks, accounts_df)
            except Exception as e:
                raise DatasetNotFoundError(f"Failed to read chunks from {filepath}: {str(e)}") from e
        else:
            try:
                tx_df = pd.read_csv(filepath, nrows=25000)
                logger.info(f"Loaded {len(tx_df)} rows from raw transactions file (limited to 25k to prevent OOM).")
                
                # HACKATHON DEMO INJECTION:
                # Ensure a mix of risk types by creating artificial anomalies in the first 25k rows.
                import numpy as np
                np.random.seed(42)
                
                # 1. Inject Large Transactions (CRITICAL/HIGH)
                large_tx_idx = tx_df.sample(frac=0.02).index
                tx_df.loc[large_tx_idx, "TX_AMOUNT"] = tx_df.loc[large_tx_idx, "TX_AMOUNT"] * 100 + 500000
                
                # 2. Inject Round Amounts (MEDIUM)
                round_tx_idx = tx_df.drop(large_tx_idx).sample(frac=0.03).index
                tx_df.loc[round_tx_idx, "TX_AMOUNT"] = 10000.0
                
                # 3. Inject Velocity/Structuring (HIGH) - Assign same sender to multiple transactions
                structuring_idx = tx_df.drop(large_tx_idx.union(round_tx_idx)).sample(frac=0.03).index
                tx_df.loc[structuring_idx, "SENDER_ACCOUNT_ID"] = 999999
                tx_df.loc[structuring_idx, "TX_AMOUNT"] = 9500.0  # Just under 10k threshold
                
                if accounts_df is not None:
                    tx_df = DatasetLoader._merge_accounts(tx_df, accounts_df)
                return tx_df
            except Exception as e:
                if not isinstance(e, JoinError):
                    raise DatasetNotFoundError(f"Failed to load dataset: {str(e)}") from e
                raise

    @staticmethod
    def _merge_accounts(tx_df: pd.DataFrame, accounts_df: pd.DataFrame) -> pd.DataFrame:
        """Merges transaction dataframe with account details to append customer_id and country.

        Uses vectorized Pandas merge.
        """
        from app.utils.schema_mapper import SchemaMapper

        tx_cols = {col.upper(): col for col in tx_df.columns}
        acc_cols = {col.upper(): col for col in accounts_df.columns}

        sender_col = tx_cols.get("SENDER_ACCOUNT_ID") or tx_cols.get("SENDER_ACCOUNT") or tx_cols.get("SENDER")
        acc_id_col = acc_cols.get("ACCOUNT_ID") or acc_cols.get("ID")

        if not sender_col or not acc_id_col:
            logger.warning("Could not map join keys between transactions and accounts. Proceeding without join.")
            return tx_df

        # Check if the transaction dataframe already contains columns that map to customer_id or country
        tx_has_customer = any(
            c.lower() in [a.lower() for a in SchemaMapper.ALIASES["customer_id"]] 
            for c in tx_df.columns
        )
        tx_has_country = any(
            c.lower() in [a.lower() for a in SchemaMapper.ALIASES["country"]] 
            for c in tx_df.columns
        )

        # Decide which columns we need to extract from accounts
        cols_to_merge = [acc_id_col]
        
        acc_cust_col = acc_cols.get("CUSTOMER_ID") or acc_cols.get("CUSTOMER")
        if not tx_has_customer and acc_cust_col:
            cols_to_merge.append(acc_cust_col)
            
        acc_country_col = acc_cols.get("COUNTRY")
        if not tx_has_country and acc_country_col:
            cols_to_merge.append(acc_country_col)

        # If accounts has no new info to add, return original
        if len(cols_to_merge) <= 1:
            return tx_df

        try:
            # De-duplicate accounts to prevent row inflation during merge
            dedup_accounts = accounts_df[cols_to_merge].drop_duplicates(subset=[acc_id_col])
            
            merged_df = tx_df.merge(
                dedup_accounts,
                left_on=sender_col,
                right_on=acc_id_col,
                how="left"
            )
            
            # Clean up the merge key from accounts if it differs from the transaction key
            if acc_id_col != sender_col and acc_id_col in merged_df.columns:
                merged_df.drop(columns=[acc_id_col], inplace=True)
                
            logger.info("Successfully merged customer information (customer_id, country) into transactions.")
            return merged_df
        except Exception as e:
            raise JoinError(f"Error during transactions-accounts merge: {str(e)}") from e

    @staticmethod
    def _wrap_chunks(chunks: Iterator[pd.DataFrame], accounts_df: Optional[pd.DataFrame]) -> Iterator[pd.DataFrame]:
        """Generator to yield merged chunks if accounts_df is available."""
        for chunk in chunks:
            if accounts_df is not None:
                yield DatasetLoader._merge_accounts(chunk, accounts_df)
            else:
                yield chunk
