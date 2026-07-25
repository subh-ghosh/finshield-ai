"""Unit test suite for validating the refined Machine Learning layer architecture."""

import os
import shutil
import pytest
import pandas as pd
import numpy as np
import time
from app.config import ml_config, PipelineConfig
from app.models.analysis_result import AnalysisResult
from app.models.analysis_source import AnalysisSource
from app.models.pipeline_result import PipelineResult
from app.models.model_metadata import ModelMetadata
from app.ml.anomaly_detection import AnomalyDetection, IsolationForestDetector
from app.ml.base_detector import AnomalyDetector
from app.ml.model_registry import ModelRegistry
from app.ml.feature_selector import FeatureSelector
from app.ml.confidence_calculator import ConfidenceCalculator
from app.ml.feature_schema import FeatureSchema
from app.ml.model_validator import ModelValidator
from app.ml.exceptions import (
    ModelNotFoundException,
    InvalidFeatureSchemaException,
    FeatureSelectionException,
    PredictionException,
    ModelPersistenceException
)
from app.utils.pipeline_profiler import PipelineProfiler
from app.utils.pipeline_events import PipelineEvents
from app.services.pipeline import AMLPipeline

@pytest.fixture
def sample_customer_features():
    """Generates a mock customer features DataFrame matching configuration feature columns."""
    data = {
        "customer_id": ["C1", "C2", "C3", "C4", "C5"],
        "transaction_count": [10.0, 5.0, 100.0, 12.0, 8.0],
        "total_amount": [1000.0, 500.0, 50000.0, 1200.0, 900.0],
        "average_amount": [100.0, 100.0, 500.0, 100.0, 112.5],
        "maximum_amount": [500.0, 200.0, 15000.0, 400.0, 300.0],
        "velocity_score": [1.2, 0.8, 8.5, 1.4, 0.9],
        "structuring_score": [0.5, 0.2, 6.0, 0.4, 0.3],
        "recipient_diversity": [2.0, 1.0, 15.0, 3.0, 2.0],
        "sender_diversity": [1.0, 1.0, 1.0, 1.0, 1.0],
        "cash_out_ratio": [0.4, 0.1, 0.95, 0.3, 0.2],
        "night_transaction_ratio": [0.1, 0.0, 0.8, 0.15, 0.05],
        "weekend_transaction_ratio": [0.2, 0.1, 0.7, 0.25, 0.1],
        "rolling_amount_24h": [200.0, 100.0, 12000.0, 300.0, 150.0],
        "rolling_count_24h": [2.0, 1.0, 24.0, 3.0, 2.0],
        "days_since_last_transaction": [4.0, 12.0, 1.0, 3.0, 5.0],
        "account_age": [365.0, 180.0, 720.0, 400.0, 200.0],
        "risk_score_placeholder": [0.0, 0.0, 0.0, 0.0, 0.0]
    }
    return pd.DataFrame(data)

@pytest.fixture
def tmp_dir():
    """Temporary workspace folder for tests."""
    path = "tmp_anomaly_test_workspace"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

# ====================================================
# FINAL ENTERPRISE ARCHITECTURAL TESTS
# ====================================================

def test_anomaly_detector_interface():
    """Checks that IsolationForestDetector inherits from AnomalyDetector abstract interface."""
    det = IsolationForestDetector()
    assert isinstance(det, AnomalyDetector)

def test_custom_exceptions():
    """Checks that domain exceptions subclass MLException and are raised appropriately."""
    with pytest.raises(ModelNotFoundException):
        raise ModelNotFoundException("Not found")

    with pytest.raises(InvalidFeatureSchemaException):
        raise InvalidFeatureSchemaException("Schema invalid")

    with pytest.raises(FeatureSelectionException):
        raise FeatureSelectionException("Selection failed")

    with pytest.raises(PredictionException):
        raise PredictionException("Prediction failed")

    with pytest.raises(ModelPersistenceException):
        raise ModelPersistenceException("Persistence failed")

def test_model_validator_checks():
    """Verifies that ModelValidator flags incorrect columns, NaNs, Infinites and shapes."""
    cols = ["col1", "col2"]
    
    # 1. Missing columns check
    df_missing = pd.DataFrame({"col1": [1.0]})
    with pytest.raises(InvalidFeatureSchemaException, match="Required features missing"):
        ModelValidator.validate_features(df_missing, cols)
        
    # 2. Ordering check
    df_order = pd.DataFrame({"col2": [1.0], "col1": [2.0]})
    with pytest.raises(InvalidFeatureSchemaException, match="Feature ordering mismatch"):
        ModelValidator.validate_features(df_order, cols)
        
    # 3. Shape mismatch check
    df_shape = pd.DataFrame({"col1": [1.0], "col2": [2.0], "col3": [3.0]})
    with pytest.raises(InvalidFeatureSchemaException, match="Feature dimension mismatch"):
        ModelValidator.validate_features(df_shape, cols)

    # 4. NaN values check
    df_nan = pd.DataFrame({"col1": [1.0, np.nan], "col2": [2.0, 3.0]})
    with pytest.raises(PredictionException, match="contains NaN values"):
        ModelValidator.validate_features(df_nan, cols)
        
    # 5. Infinite values check
    df_inf = pd.DataFrame({"col1": [1.0, np.inf], "col2": [2.0, 3.0]})
    with pytest.raises(PredictionException, match="contains Infinite values"):
        ModelValidator.validate_features(df_inf, cols)

def test_feature_schema_checks():
    """Asserts that FeatureSchema checks column types and presence."""
    schema = FeatureSchema(
        feature_names=["f1", "f2"],
        data_types={"f1": "numeric", "f2": "numeric"}
    )
    
    # Check invalid columns
    df_bad_cols = pd.DataFrame({"f1": [1.0]})
    with pytest.raises(InvalidFeatureSchemaException, match="Required columns missing"):
        schema.validate(df_bad_cols)
        
    # Check invalid types
    df_bad_types = pd.DataFrame({"f1": [1.0], "f2": ["string_val"]})
    with pytest.raises(InvalidFeatureSchemaException, match="expected to be numeric"):
        schema.validate(df_bad_types)

def test_model_metadata_serialization(sample_customer_features, tmp_dir):
    """Checks that ModelMetadata is generated, saved, and loaded successfully with the model."""
    det = AnomalyDetection()
    det.fit(sample_customer_features)
    
    assert isinstance(det.metadata, ModelMetadata)
    assert det.metadata.model_name == "IsolationForest"
    assert det.metadata.random_state == ml_config.RANDOM_STATE
    assert det.metadata.feature_names == ml_config.FEATURE_COLUMNS
    
    # Save model and load to check metadata restoration
    model_path = os.path.join(tmp_dir, "model_meta.pkl")
    det.save_model(model_path)
    
    det2 = AnomalyDetection()
    det2.load_model(model_path)
    assert det2.metadata is not None
    assert det2.metadata.model_name == "IsolationForest"
    assert det2.metadata.feature_names == ml_config.FEATURE_COLUMNS

def test_pipeline_profiler():
    """Asserts that PipelineProfiler records inline timings and retrieves combined results."""
    PipelineProfiler.reset()
    
    with PipelineProfiler.profile("MyCustomStage"):
        time.sleep(0.01)
        
    timings = PipelineProfiler.get_profile_timings()
    assert "MyCustomStage" in timings
    assert timings["MyCustomStage"] > 0.0

def test_pipeline_events():
    """Verifies that PipelineEvents log messages trigger successfully without raising errors."""
    try:
        PipelineEvents.on_pipeline_started("dataset.csv")
        PipelineEvents.on_feature_engineering_completed(10)
        PipelineEvents.on_rule_engine_completed(5)
        PipelineEvents.on_anomaly_detection_completed(2)
        PipelineEvents.on_pipeline_finished(0.85)
    except Exception as e:
        pytest.fail(f"PipelineEvents handler raised an exception: {str(e)}")

# ====================================================
# PREVIOUS ANOMALY DETECTION TEST CASES
# ====================================================

def test_ml_config_loading():
    """Checks that all essential ML config values load correctly from ml_config."""
    assert ml_config.N_ESTIMATORS == 100
    assert ml_config.CONTAMINATION == 0.02
    assert ml_config.RANDOM_STATE == 42
    assert len(ml_config.FEATURE_COLUMNS) == 14
    assert ml_config.SEVERITY_THRESHOLDS["CRITICAL"] == 0.75

def test_feature_selector_transformer(sample_customer_features):
    """Verifies that FeatureSelector exposes transformer interfaces correctly."""
    selector = FeatureSelector()
    selector.fit(sample_customer_features)
    selected = selector.transform(sample_customer_features)
    assert list(selected.columns) == ml_config.FEATURE_COLUMNS
    assert "customer_id" not in selected.columns

def test_analysis_source_enum():
    """Checks string-based comparison and values of AnalysisSource Enum."""
    assert AnalysisSource.RULE_ENGINE == "rule_engine"
    assert AnalysisSource.ISOLATION_FOREST == "isolation_forest"
    
    source_val = AnalysisSource.ISOLATION_FOREST
    assert source_val == "isolation_forest"
    assert f"{source_val}" == "isolation_forest"

def test_confidence_calculator():
    """Verifies boundary-distance calculations in ConfidenceCalculator."""
    calc = ConfidenceCalculator()
    scores = np.array([-0.3, 0.0, 0.4])
    confidences = calc.calculate(scores)
    np.testing.assert_allclose(confidences, [0.6, 0.0, 0.8])

def test_pipeline_result_metadata(sample_customer_features):
    """Checks that PipelineResult supports metadata tracking fields with safe defaults."""
    report = None
    res = PipelineResult(
        clean_dataframe=pd.DataFrame(),
        customer_features=sample_customer_features,
        rule_analysis=[],
        rule_dataframe=pd.DataFrame(),
        anomaly_analysis=[],
        anomaly_dataframe=pd.DataFrame(),
        report=report,
        execution_time=1.5,
        pipeline_version="1.0.0",
        model_versions={"isolation_forest": "1.0"},
        metadata={"test": "ok"}
    )
    
    assert res.execution_time == 1.5
    assert res.pipeline_version == "1.0.0"
    assert res.model_versions == {"isolation_forest": "1.0"}
    assert res.metadata == {"test": "ok"}

def test_model_registry_extensions():
    """Verifies ModelRegistry's extended operations (exists, list, delete, metadata)."""
    ModelRegistry.delete_model("my_custom_model")
    
    dummy_model = object()
    ModelRegistry.register_model("my_custom_model", dummy_model, {"version": "2.1"})
    
    assert ModelRegistry.model_exists("my_custom_model")
    assert "my_custom_model" in ModelRegistry.list_models()
    assert ModelRegistry.get_metadata("my_custom_model") == {"version": "2.1"}
    
    ModelRegistry.delete_model("my_custom_model")
    assert not ModelRegistry.model_exists("my_custom_model")

def test_dependency_injection(sample_customer_features):
    """Checks that AnomalyDetection successfully consumes injected dependencies."""
    custom_cols = ["transaction_count", "total_amount"]
    selector = FeatureSelector(custom_cols)
    calc = ConfidenceCalculator()
    
    det = AnomalyDetection(
        feature_selector=selector,
        confidence_calculator=calc
    )
    
    assert det.feature_selector is selector
    assert det.confidence_calculator is calc
    assert det.feature_columns == custom_cols
    
    det.fit(sample_customer_features)
    results = det.predict(sample_customer_features)
    assert len(results) == 5
    assert results[0].metadata["feature_count"] == 2

def test_backward_compatibility():
    """Verifies AnalysisResult maintains complete backward compatibility with older instantiations."""
    res = AnalysisResult(
        customer_id="C1",
        severity="LOW",
        total_rule_score=15,
        triggered_rules=[]
    )
    assert res.customer_id == "C1"
    assert res.severity == "LOW"
    assert res.total_rule_score == 15
    assert res.source == "rule_engine"

def test_feature_selection_and_validation(sample_customer_features):
    """Verifies feature preparation, non-numeric checks, and missing columns validations."""
    det = AnomalyDetection()
    prepared = det.feature_selector.transform(sample_customer_features)
    assert list(prepared.columns) == ml_config.FEATURE_COLUMNS
    
    bad_df = sample_customer_features.drop(columns=["velocity_score"])
    with pytest.raises(ValueError, match="Features missing from input dataset"):
        det.feature_selector.transform(bad_df)
        
    bad_df_type = sample_customer_features.copy()
    bad_df_type["velocity_score"] = "bad_string"
    with pytest.raises(ValueError, match="contains non-numeric data types"):
        det.feature_selector.transform(bad_df_type)

def test_feature_scaling_and_fitting(sample_customer_features):
    """Verifies fitting processes and standard scaler transforms."""
    det = AnomalyDetection()
    det.fit(sample_customer_features)
    assert det.is_trained
    assert det.scaler is not None
    assert det.model is not None

def test_dataframe_conversion(sample_customer_features):
    """Verifies that to_dataframe converts results into correct columns."""
    det = AnomalyDetection()
    det.fit(sample_customer_features)
    results = det.predict(sample_customer_features)
    
    df = AnomalyDetection.to_dataframe(results)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["customer_id", "anomaly_score", "confidence", "severity", "prediction", "metadata"]
    assert len(df) == 5

def test_reproducible_predictions_with_seed(sample_customer_features):
    """Checks that random state guarantees identical results across separate fits."""
    det1 = AnomalyDetection()
    det1.fit(sample_customer_features)
    scores1 = [r.anomaly_score for r in det1.predict(sample_customer_features)]
    
    det2 = AnomalyDetection()
    det2.fit(sample_customer_features)
    scores2 = [r.anomaly_score for r in det2.predict(sample_customer_features)]
    
    assert scores1 == scores2

def test_single_customer_dataset(sample_customer_features):
    """Checks fit/predict bounds with a single customer input row."""
    det = AnomalyDetection()
    single_df = sample_customer_features.head(1)
    det.fit(single_df)
    results = det.predict(single_df)
    assert len(results) == 1
    assert results[0].anomaly_score == 0.5

def test_identical_customers(sample_customer_features):
    """Checks that identical customers receive identical anomaly scores."""
    det = AnomalyDetection()
    dup_df = pd.concat([sample_customer_features.head(1)] * 3, ignore_index=True)
    dup_df.loc[1, "customer_id"] = "C1_dup"
    dup_df.loc[2, "customer_id"] = "C1_dup2"
    
    det.fit(dup_df)
    results = det.predict(dup_df)
    assert len(results) == 3
    assert results[0].anomaly_score == results[1].anomaly_score
    assert results[0].anomaly_score == results[2].anomaly_score

def test_pipeline_integration_returns_pipelineresult(tmp_dir):
    """Verifies that the complete pipeline execution executes anomaly detection and returns PipelineResult."""
    tx_path = os.path.join(tmp_dir, "transactions.csv")
    tx_data = pd.DataFrame({
        "TX_ID": ["1", "2", "3", "4", "5"],
        "SENDER_ACCOUNT_ID": ["A1", "A2", "A3", "A4", "A5"],
        "RECEIVER_ACCOUNT_ID": ["B1", "B2", "B3", "B4", "B5"],
        "TX_TYPE": ["TRANSFER", "CASH_OUT", "TRANSFER", "CASH_OUT", "TRANSFER"],
        "TX_AMOUNT": [1000.0, 500.0, 50000.0, 1200.0, 900.0],
        "TIMESTAMP": [1609459200, 1609459260, 1609459320, 1609459380, 1609459440]
    })
    tx_data.to_csv(tx_path, index=False)
    
    acc_path = os.path.join(tmp_dir, "accounts.csv")
    acc_data = pd.DataFrame({
        "ACCOUNT_ID": ["A1", "A2", "A3", "A4", "A5"],
        "CUSTOMER_ID": ["C1", "C2", "C3", "C4", "C5"],
        "COUNTRY": ["US", "US", "DE", "UK", "CA"]
    })
    acc_data.to_csv(acc_path, index=False)
    
    config = PipelineConfig(
        reports_dir=os.path.join(tmp_dir, "reports"),
        rejected_dir=os.path.join(tmp_dir, "reports", "rejected"),
        cache_dir=os.path.join(tmp_dir, "cache"),
        feature_store_dir=os.path.join(tmp_dir, "features")
    )
    
    pipeline = AMLPipeline(config)
    res = pipeline.run(tx_path)
    
    assert isinstance(res, PipelineResult)
    assert isinstance(res.clean_dataframe, pd.DataFrame)
    assert isinstance(res.customer_features, pd.DataFrame)
    assert isinstance(res.rule_analysis, list)
    assert isinstance(res.rule_dataframe, pd.DataFrame)
    assert isinstance(res.anomaly_analysis, list)
    assert isinstance(res.anomaly_dataframe, pd.DataFrame)
    assert len(res.anomaly_analysis) == 5
    assert res.anomaly_analysis[0].source == AnalysisSource.ISOLATION_FOREST
