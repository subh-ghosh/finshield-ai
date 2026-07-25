"""Unit test suite for validating all aspects of the AML Preprocessing Platform."""

import os
import shutil
import pytest
import pandas as pd
import numpy as np
from app.config import PipelineConfig, PIPELINE_VERSION, CANONICAL_COLUMNS
from app.contracts.data_contract import DataContractValidator
from app.utils.exceptions import InvalidSchemaError, MissingColumnError
from app.utils.schema_mapper import SchemaMapper
from app.services.cache_manager import CacheManager
from app.services.feature_store import FeatureStore
from app.services.feature_engineering import FeatureEngineering
from app.services.preprocessing import AMLPreprocessor
from app.services.pipeline import AMLPipeline

@pytest.fixture
def sample_raw_data():
    """Generates a representative raw dataset containing typical data issues."""
    data = {
        "TX_ID": ["1", "2", "3", "3", "4", "5", "6"],
        "SENDER_ACCOUNT_ID": ["A_100", "A_101", "A_102", "A_102", "A_103", None, "A_105"],
        "RECEIVER_ACCOUNT_ID": ["B_200", "B_201", "B_202", "B_202", None, "B_204", "B_205"],
        "TX_TYPE": ["TRANSFER", "CASH_OUT", "CASH_IN", "CASH_IN", "TRANSFER", "CASH_OUT", "TRANSFER"],
        "TX_AMOUNT": [100.50, -50.0, 200.0, 200.0, 150.0, 300.0, np.nan],
        "TIMESTAMP": [1609459200, 1609459260, 1609459320, 1609459320, 1609459380, 1609459440, 1609459500],
        "CUSTOMER_ID": ["C_001", "C_002", "C_003", "C_003", "C_004", "C_005", "C_006"],
        "COUNTRY": ["US", "US", None, None, "UK", "CA", "US"],
        "CURRENCY": ["USD", "USD", "USD", "USD", "GBP", "CAD", "USD"]
    }
    return pd.DataFrame(data)

@pytest.fixture
def tmp_dir():
    """Provides a clean temporary directory for files, automatically cleaned up after use."""
    path = "tmp_test_dir"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

def test_pipeline_config():
    """Validates configuration types and instantiation constraints."""
    config = PipelineConfig()
    assert config.remove_duplicates is True
    assert config.use_cache is True
    
    with pytest.raises(TypeError):
        # Trigger type verification logic
        PipelineConfig(remove_duplicates="not_a_boolean")

def test_schema_mapper():
    """Checks schema mapping alias detection."""
    raw_columns = ["TX_ID", "SENDER_ACCOUNT_ID", "RECEIVER_ACCOUNT_ID", "TX_TYPE", "TX_AMOUNT", "TIMESTAMP", "CUSTOMER_ID", "COUNTRY", "CURRENCY"]
    normalized = [c.lower() for c in raw_columns]
    
    mappings = SchemaMapper.get_mappings(normalized)
    
    assert mappings["tx_id"] == "transaction_id"
    assert mappings["tx_amount"] == "amount"
    assert mappings["sender_account_id"] == "sender_account"
    assert mappings["receiver_account_id"] == "receiver_account"

def test_data_contract_validator():
    """Verifies that DataContractValidator raises clean schema exception triggers."""
    # Build clean canonical DataFrame
    valid_df = pd.DataFrame({
        "transaction_id": ["1", "2"],
        "customer_id": ["C1", "C2"],
        "sender_account": ["A1", "A2"],
        "receiver_account": ["B1", "B2"],
        "timestamp": pd.to_datetime([1609459200, 1609459260], unit="s"),
        "amount": np.array([100.0, 200.0], dtype=np.float32),
        "currency": pd.Categorical(["USD", "USD"]),
        "country": pd.Categorical(["US", "US"]),
        "transaction_type": pd.Categorical(["TRANSFER", "TRANSFER"])
    })
    
    # Must succeed without throwing
    DataContractValidator.validate(valid_df)
    
    # Drop column to fail validation
    invalid_df = valid_df.drop(columns=["amount"])
    with pytest.raises(MissingColumnError):
        DataContractValidator.validate(invalid_df)
        
    # Check null violation
    invalid_null_df = valid_df.copy()
    invalid_null_df.loc[0, "customer_id"] = np.nan
    with pytest.raises(InvalidSchemaError) as exc:
        DataContractValidator.validate(invalid_null_df)
    assert "contains 1 nulls" in str(exc.value)

def test_preprocessor_stages(sample_raw_data):
    """Verifies individual preprocessor stages execute correctly."""
    preprocessor = AMLPreprocessor()
    preprocessor.raw_df = sample_raw_data.copy()
    preprocessor.df = sample_raw_data.copy()
    preprocessor.rows_loaded = len(sample_raw_data)
    
    # Normalize
    df = preprocessor.normalize_column_names(preprocessor.df)
    assert "tx_id" in df.columns
    
    # Schema Map
    df = preprocessor.map_schema(df)
    assert "transaction_id" in df.columns
    assert "amount" in df.columns
    
    # Validation
    preprocessor.validate_schema(df)
    
    # Types
    df = preprocessor.convert_dtypes(df)
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])
    assert pd.api.types.is_float_dtype(df["amount"])
    
    # Cleaning missing values
    df = preprocessor.clean_missing_values(df)
    # Row 4 (missing receiver_account), Row 5 (missing sender_account), Row 6 (missing amount)
    assert len(preprocessor.missing_df) == 3
    
    # Duplicates
    df = preprocessor.remove_duplicates(df)
    # Row 3 (id '3') is a duplicate of Row 2 (id '3')
    assert len(preprocessor.duplicate_df) == 1
    
    # Amounts and dates
    df = preprocessor.validate_amounts(df)
    # Row 1 has negative amount -50.0
    assert len(preprocessor.invalid_df) == 1
    
    # Sort and return
    df = preprocessor.sort_by_timestamp(df)
    assert len(df) == 2
    assert df.loc[0, "customer_id"] == "C_001"

def test_feature_engineering():
    """Verifies that FeatureEngineering correctly aggregates by customer and creates columns."""
    clean_df = pd.DataFrame({
        "transaction_id": ["1", "2", "3"],
        "customer_id": ["C1", "C2", "C1"],
        "sender_account": ["A1", "A2", "A1"],
        "receiver_account": ["B1", "B2", "B3"],
        "timestamp": pd.to_datetime([1609459200, 1609459260, 1609459320], unit="s"),
        "amount": np.array([100.0, 200.0, 50.0], dtype=np.float32),
        "currency": pd.Categorical(["USD", "USD", "USD"]),
        "country": pd.Categorical(["US", "US", "US"]),
        "transaction_type": pd.Categorical(["TRANSFER", "TRANSFER", "TRANSFER"])
    })
    
    fe = FeatureEngineering()
    feat_df = fe.run(clean_df)
    
    # Should have exactly two customers (C1, C2)
    assert len(feat_df) == 2
    assert list(feat_df["customer_id"]) == ["C1", "C2"]
    
    # Aggregate checks for C1
    c1_row = feat_df[feat_df["customer_id"] == "C1"].iloc[0]
    assert c1_row["transaction_count"] == 2
    assert c1_row["total_amount"] == 150.0
    assert c1_row["average_amount"] == 75.0
    
    # Verify expected placeholders are present
    assert "structuring_score" in feat_df.columns
    assert "velocity_score" in feat_df.columns
    assert "days_since_last_transaction" in feat_df.columns

def test_cache_manager(sample_raw_data, tmp_dir):
    """Checks CacheManager checks, hits, hashes, and saving."""
    file_path = os.path.join(tmp_dir, "raw_tx.csv")
    sample_raw_data.to_csv(file_path, index=False)
    
    file_hash = CacheManager.calculate_file_hash(file_path)
    assert len(file_hash) == 32
    
    # Miss
    assert CacheManager.load_cached_dataset(file_hash, tmp_dir) is None
    
    # Save
    data = pd.DataFrame({"amount": [1.0, 2.0]})
    CacheManager.save_to_cache(data, file_hash, tmp_dir)
    
    # Hit
    cached = CacheManager.load_cached_dataset(file_hash, tmp_dir)
    assert cached is not None
    assert list(cached["amount"]) == [1.0, 2.0]

def test_feature_store(tmp_dir):
    """Checks Feature Store save, load, update, and clear interfaces for customer features."""
    fs = FeatureStore(tmp_dir)
    data = pd.DataFrame({"customer_id": ["C1"], "feat_a": [1.0]})
    
    fs.save(data)
    
    loaded = fs.load()
    assert loaded is not None
    assert list(loaded["feat_a"]) == [1.0]
    assert list(loaded["customer_id"]) == ["C1"]
    
    # Update
    data_up = pd.DataFrame({"customer_id": ["C1"], "feat_a": [5.0]})
    fs.update(data_up)
    
    loaded_up = fs.load()
    assert loaded_up.loc[0, "feat_a"] == 5.0
    
    # Clear
    fs.clear()
    assert fs.load() is None

def test_pipeline_execution(sample_raw_data, tmp_dir):
    """Verifies complete end-to-end pipeline run, profile saving, and context tracking."""
    tx_path = os.path.join(tmp_dir, "transactions.csv")
    acc_path = os.path.join(tmp_dir, "accounts.csv")
    
    sample_raw_data.to_csv(tx_path, index=False)
    
    # Create accounts schema mapping file
    accounts = {
        "ACCOUNT_ID": ["A_100", "A_101", "A_102", "A_103", "A_104", "A_105"],
        "CUSTOMER_ID": ["C_001", "C_002", "C_003", "C_004", "C_005", "C_006"],
        "COUNTRY": ["US", "US", "DE", "UK", "CA", "US"]
    }
    pd.DataFrame(accounts).to_csv(acc_path, index=False)
    
    config = PipelineConfig(
        reports_dir=os.path.join(tmp_dir, "reports"),
        rejected_dir=os.path.join(tmp_dir, "reports", "rejected"),
        cache_dir=os.path.join(tmp_dir, "cache"),
        feature_store_dir=os.path.join(tmp_dir, "features")
    )
    
    pipeline = AMLPipeline(config)
    res = pipeline.run(tx_path)
    clean_df = res.clean_dataframe
    customer_features = res.customer_features
    
    # Assert contract outputs
    assert len(clean_df) > 0
    for col in CANONICAL_COLUMNS:
        assert col in clean_df.columns
        
    # Check customer features output
    assert len(customer_features) > 0
    assert "customer_id" in customer_features.columns
    assert "average_amount" in customer_features.columns
        
    # Check reports and metadata files
    assert os.path.exists(os.path.join(config.reports_dir, "metadata.json"))
    assert os.path.exists(os.path.join(config.reports_dir, "dataset_profile.json"))
    assert os.path.exists(os.path.join(config.rejected_dir, "duplicate_rows.csv"))
    
    # Check context metadata
    assert pipeline.context is not None
    assert pipeline.context.dataset_name == "transactions.csv"
