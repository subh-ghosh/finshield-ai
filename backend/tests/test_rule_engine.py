"""Unit test suite for validating all aspects of the AML Rule Engine component."""

import os
import shutil
import pytest
import pandas as pd
import numpy as np
from app.config.rule_thresholds import (
    HIGH_VELOCITY_THRESHOLD, HIGH_VELOCITY_SCORE,
    STRUCTURING_THRESHOLD, STRUCTURING_SCORE,
    LARGE_TRANSACTION_THRESHOLD, LARGE_TRANSACTION_SCORE
)
from app.models.rule_evaluation import RuleEvaluation
from app.models.triggered_rule import TriggeredRule
from app.models.analysis_result import AnalysisResult
from app.rules.base_rule import BaseRule
from app.rules.velocity_rule import VelocityRule
from app.rules.structuring_rule import StructuringRule
from app.services.rule_engine import RuleEngine
from app.services.pipeline import AMLPipeline
from app.config import PipelineConfig

@pytest.fixture
def clean_test_customer():
    """Generates customer features that trigger zero rules."""
    return pd.Series({
        "customer_id": "C_CLEAN",
        "velocity_score": 1.0,
        "structuring_score": 2.0,
        "smurfing_score": 0.0,
        "round_amount_ratio": 0.1,
        "cash_out_ratio": 0.2,
        "recipient_diversity": 2.0,
        "days_since_last_transaction": 5.0,
        "maximum_amount": 500.0
    })

@pytest.fixture
def high_risk_customer():
    """Generates customer features triggering Velocity, Structuring, and Large Transaction rules."""
    return pd.Series({
        "customer_id": "C_SUSPICIOUS",
        "velocity_score": 8.0,        # > 5.0 (High Velocity)
        "structuring_score": 7.5,     # > 5.0 (Structuring)
        "smurfing_score": 0.0,
        "round_amount_ratio": 0.1,
        "cash_out_ratio": 0.2,
        "recipient_diversity": 2.0,
        "days_since_last_transaction": 5.0,
        "maximum_amount": 25000.0     # > 10000.0 (Large Transaction)
    })

@pytest.fixture
def tmp_dir():
    """Clean temp directory for pipeline output files."""
    path = "tmp_rule_engine_test_dir"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

def test_rule_inheritance_and_registration():
    """Verifies rule registration and abstract BaseRule inheritance."""
    engine = RuleEngine()
    assert len(engine.rules) == 8
    for rule in engine.rules:
        assert isinstance(rule, BaseRule)

def test_no_rules_triggered(clean_test_customer):
    """Verifies outputs and severity classification when 0 rules trigger."""
    engine = RuleEngine()
    features_df = pd.DataFrame([clean_test_customer])
    results = engine.run(features_df)
    
    assert len(results) == 1
    res: AnalysisResult = results[0]
    assert res.customer_id == "C_CLEAN"
    assert res.total_rule_score == 0
    assert res.severity == "LOW"
    assert len(res.triggered_rules) == 0

def test_multiple_rules_triggered(high_risk_customer):
    """Checks accumulated score, severity brackets, and structured evidence on match."""
    engine = RuleEngine()
    features_df = pd.DataFrame([high_risk_customer])
    results = engine.run(features_df)
    
    assert len(results) == 1
    res: AnalysisResult = results[0]
    assert res.customer_id == "C_SUSPICIOUS"
    
    expected_score = HIGH_VELOCITY_SCORE + STRUCTURING_SCORE + LARGE_TRANSACTION_SCORE
    assert res.total_rule_score == expected_score
    assert res.severity == "HIGH"  # Score of 55 lies in 40-69 bracket
    assert len(res.triggered_rules) == 3
    
    # Inspect individual triggers
    triggered_ids = [tr.rule_id for tr in res.triggered_rules]
    assert "RULE_VELOCITY" in triggered_ids
    assert "RULE_STRUCTURING" in triggered_ids
    assert "RULE_LARGE_TRANSACTION" in triggered_ids
    
    velocity_tr = [tr for tr in res.triggered_rules if tr.rule_id == "RULE_VELOCITY"][0]
    assert velocity_tr.score == HIGH_VELOCITY_SCORE
    assert velocity_tr.evidence["velocity_score"] == 8.0
    assert velocity_tr.evidence["threshold"] == HIGH_VELOCITY_THRESHOLD

def test_dataframe_conversion(high_risk_customer):
    """Checks conversions from structured dataclass outputs to debug dataframes."""
    engine = RuleEngine()
    features_df = pd.DataFrame([high_risk_customer])
    results = engine.run(features_df)
    
    df = RuleEngine.to_dataframe(results)
    assert len(df) == 1
    assert df.loc[0, "customer_id"] == "C_SUSPICIOUS"
    assert df.loc[0, "rule_score"] == 55
    assert df.loc[0, "severity"] == "HIGH"
    assert "RULE_VELOCITY" in df.loc[0, "triggered_rules"]
    assert "velocity_score" in df.loc[0, "rule_evidence"][0]

def test_severity_classification_brackets():
    """Asserts that classification thresholds align with spec brackets."""
    assert RuleEngine._classify_severity(0) == "LOW"
    assert RuleEngine._classify_severity(19) == "LOW"
    assert RuleEngine._classify_severity(20) == "MEDIUM"
    assert RuleEngine._classify_severity(39) == "MEDIUM"
    assert RuleEngine._classify_severity(40) == "HIGH"
    assert RuleEngine._classify_severity(69) == "HIGH"
    assert RuleEngine._classify_severity(70) == "CRITICAL"
    assert RuleEngine._classify_severity(100) == "CRITICAL"

def test_pipeline_integration(tmp_dir):
    """Checks that the RuleEngine integrates into the overall AMLPipeline."""
    tx_path = os.path.join(tmp_dir, "transactions.csv")
    tx_data = pd.DataFrame({
        "TX_ID": ["1", "2"],
        "SENDER_ACCOUNT_ID": ["A1", "A2"],
        "RECEIVER_ACCOUNT_ID": ["B1", "B2"],
        "TX_TYPE": ["TRANSFER", "CASH_OUT"],
        "TX_AMOUNT": [25000.0, 100.0],  # Trigger LargeTransaction (C1 has max 25000.0)
        "TIMESTAMP": [1609459200, 1609459260]
    })
    tx_data.to_csv(tx_path, index=False)
    
    acc_path = os.path.join(tmp_dir, "accounts.csv")
    acc_data = pd.DataFrame({
        "ACCOUNT_ID": ["A1", "A2"],
        "CUSTOMER_ID": ["C1", "C2"],
        "COUNTRY": ["US", "US"]
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
    clean_df = res.clean_dataframe
    feat_df = res.customer_features
    analysis = res.rule_analysis
    rule_df = res.rule_dataframe
    
    assert isinstance(clean_df, pd.DataFrame)
    assert isinstance(feat_df, pd.DataFrame)
    assert isinstance(analysis, list)
    assert isinstance(rule_df, pd.DataFrame)
    assert len(analysis) == 2
    
    c1_res = [res for res in analysis if res.customer_id == "C1"][0]
    assert c1_res.total_rule_score == LARGE_TRANSACTION_SCORE
    assert c1_res.triggered_rules[0].rule_id == "RULE_LARGE_TRANSACTION"
