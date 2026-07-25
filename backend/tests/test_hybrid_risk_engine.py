"""Unit and integration test suite for the Enterprise Hybrid Risk Engine."""

import os
import time
import shutil
import pytest
import numpy as np
import pandas as pd
from app.config import ml_config, PipelineConfig
from app.ml.interfaces.behavioral_risk_analyzer import IBehavioralRiskAnalyzer
from app.ml.interfaces.fusion_strategy import IFusionStrategy
from app.ml.interfaces.recommendation_engine import IRecommendationStrategy, IRecommendationEngine
from app.ml.interfaces.hybrid_risk_engine import IHybridRiskEngine
from app.ml.behavioral_risk_analyzer import BehavioralRiskAnalyzer
from app.ml.weighted_fusion_strategy import WeightedFusionStrategy
from app.ml.deterministic_recommendation_strategy import DeterministicRecommendationStrategy
from app.ml.recommendation_engine import RecommendationEngine
from app.ml.hybrid_risk_engine import HybridRiskEngine
from app.models.analysis_result import AnalysisResult
from app.models.analysis_source import AnalysisSource
from app.models.pipeline_context import PipelineContext
from app.models.score_breakdown import ScoreBreakdown
from app.models.risk_factor import RiskFactor
from app.models.explanation import Explanation
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.pipeline_result import PipelineResult
from app.services.pipeline import AMLPipeline

@pytest.fixture
def mock_pipeline_context():
    """Generates a standard PipelineContext mock for testing."""
    features_df = pd.DataFrame({
        "customer_id": ["C_001", "C_002", "C_003"],
        "transaction_count": [5.0, 1.0, 50.0],
        "total_amount": [500.0, 100.0, 10000.0],
        "average_amount": [100.0, 100.0, 200.0],
        "maximum_amount": [200.0, 100.0, 5000.0],
        "velocity_score": [1.5, 0.5, 9.5],
        "structuring_score": [0.5, 0.1, 8.5],
        "recipient_diversity": [2.0, 1.0, 14.0],
        "sender_diversity": [1.0, 1.0, 4.0],
        "cash_out_ratio": [0.3, 0.05, 0.95],
        "night_transaction_ratio": [0.1, 0.0, 0.7],
        "weekend_transaction_ratio": [0.2, 0.1, 0.6],
        "rolling_amount_24h": [100.0, 10.0, 8000.0],
        "rolling_count_24h": [1.0, 1.0, 15.0],
        "days_since_last_transaction": [4.0, 15.0, 1.0]
    })
    
    rule_results = [
        AnalysisResult(customer_id="C_001", total_rule_score=10, severity="MEDIUM", triggered_rules=[]),
        AnalysisResult(customer_id="C_002", total_rule_score=0, severity="LOW", triggered_rules=[]),
        AnalysisResult(customer_id="C_003", total_rule_score=60, severity="CRITICAL", triggered_rules=[])
    ]
    
    ml_results = [
        AnalysisResult(
            customer_id="C_001",
            severity="LOW",
            source=AnalysisSource.ISOLATION_FOREST,
            score=0.15,
            confidence=0.9,
            anomaly_score=0.15,
            metadata={"prediction": 1}
        ),
        AnalysisResult(
            customer_id="C_002",
            severity="LOW",
            source=AnalysisSource.ISOLATION_FOREST,
            score=0.1,
            confidence=0.95,
            anomaly_score=0.1,
            metadata={"prediction": 1}
        ),
        AnalysisResult(
            customer_id="C_003",
            severity="CRITICAL",
            source=AnalysisSource.ISOLATION_FOREST,
            score=0.85,
            confidence=0.8,
            anomaly_score=0.85,
            metadata={"prediction": -1}
        )
    ]
    
    return PipelineContext(
        customer_features=features_df,
        rule_results=rule_results,
        ml_results=ml_results,
        pipeline_version="1.0.0",
        dataset_info={"name": "test_dataset.csv"}
    )

@pytest.fixture
def tmp_dir():
    """Temporary workspace folder for tests."""
    path = "tmp_hybrid_risk_test_workspace"
    os.makedirs(path, exist_ok=True)
    yield path
    if os.path.exists(path):
        shutil.rmtree(path)

# ====================================================
# UNIT TESTS FOR NEW DECOUPLED ARCHITECTURE
# ====================================================

def test_interface_hierarchies():
    """Verifies that implementations comply with strict interface definitions."""
    assert issubclass(BehavioralRiskAnalyzer, IBehavioralRiskAnalyzer)
    assert issubclass(WeightedFusionStrategy, IFusionStrategy)
    assert issubclass(DeterministicRecommendationStrategy, IRecommendationStrategy)
    assert issubclass(RecommendationEngine, IRecommendationEngine)
    assert issubclass(HybridRiskEngine, IHybridRiskEngine)

def test_behavioral_risk_analyzer_loading(mock_pipeline_context):
    """Verifies BehavioralRiskAnalyzer calculates custom weights and normalizations from configuration."""
    analyzer = BehavioralRiskAnalyzer()
    
    row = mock_pipeline_context.customer_features.iloc[0]
    score, breakdown, factors = analyzer.analyze(row)
    
    assert 0.0 <= score <= 1.0
    assert "velocity_score" in breakdown
    assert "cash_out_ratio" in breakdown
    assert breakdown["velocity_score"] == pytest.approx(0.15)
    
    for f in factors:
        assert isinstance(f, RiskFactor)
        assert f.source == "BEHAVIORAL"

def test_behavioral_risk_analyzer_missing_columns():
    """Defensively verifies BehavioralRiskAnalyzer outputs safely when input columns are missing."""
    analyzer = BehavioralRiskAnalyzer()
    row = pd.Series({"customer_id": "C_empty"})
    
    score, breakdown, factors = analyzer.analyze(row)
    assert score == 0.0
    assert len(factors) == 0
    assert breakdown["velocity_score"] == 0.0

def test_weighted_fusion_strategy_validation():
    """Asserts that WeightedFusionStrategy rejects invalid, negative, or unnormalized configuration weights."""
    with pytest.raises(ValueError, match="weights must sum to approximately 1.0"):
        WeightedFusionStrategy(weights={"rule_engine": 0.5, "isolation_forest": 0.2})
        
    with pytest.raises(ValueError, match="cannot be negative"):
        WeightedFusionStrategy(weights={"rule_engine": 1.2, "isolation_forest": -0.2, "behavioural": 0.0})

def test_weighted_fusion_strategy_math():
    """Verifies WeightedFusionStrategy mathematical computation."""
    strategy = WeightedFusionStrategy(weights={"rule_engine": 0.5, "isolation_forest": 0.3, "behavioural": 0.2})
    score = strategy.fuse(0.8, 0.4, 0.6)
    assert score == pytest.approx(0.64)

def test_deterministic_recommendation_strategy():
    """Checks score thresholds mapping inside DeterministicRecommendationStrategy."""
    strategy = DeterministicRecommendationStrategy()
    
    assert strategy.determine_recommendation(0.80) == "Immediate Investigation"
    assert strategy.determine_recommendation(0.55) == "File SAR Recommendation"
    assert strategy.determine_recommendation(0.38) == "Escalate Investigation"
    assert strategy.determine_recommendation(0.28) == "Manual Review"
    assert strategy.determine_recommendation(0.10) == "Continue Monitoring"

def test_recommendation_engine_delegates():
    """Asserts RecommendationEngine delegates execution to its injected strategy."""
    class DummyStrategy(IRecommendationStrategy):
        def determine_recommendation(self, score: float) -> str:
            return "Test Passed"
            
    engine = RecommendationEngine(strategy=DummyStrategy())
    assert engine.generate(0.5) == "Test Passed"

def test_score_breakdown_model():
    """Checks ScoreBreakdown dataclass parameters integrity."""
    weights = {"rule_engine": 0.6, "isolation_forest": 0.3, "behavioural": 0.1}
    breakdown = ScoreBreakdown(
        rule_score=0.4,
        ml_score=0.2,
        behavioral_score=0.5,
        overall_score=0.35,
        weights_used=weights
    )
    
    assert breakdown.rule_score == 0.4
    assert breakdown.overall_score == 0.35
    assert breakdown.weights_used == weights

def test_pipeline_context_aggregation(mock_pipeline_context):
    """Verifies PipelineContext correctly aggregates and exposes metadata attributes."""
    context = mock_pipeline_context
    assert context.pipeline_version == "1.0.0"
    assert context.dataset_info == {"name": "test_dataset.csv"}
    assert len(context.customer_features) == 3

def test_hybrid_risk_engine_orchestrates(mock_pipeline_context):
    """Verifies HybridRiskEngine orchestrator runs sub-components and generates unified HybridRiskResult listings."""
    engine = HybridRiskEngine()
    results = engine.evaluate(mock_pipeline_context)
    
    assert len(results) == 3
    for res in results:
        assert isinstance(res, HybridRiskResult)
        assert res.engine_name == "HybridRiskEngine"
        assert res.score_breakdown.overall_score == res.overall_risk_score
        assert isinstance(res.explanation, Explanation)
        assert isinstance(res.score_breakdown, ScoreBreakdown)

def test_hybrid_risk_engine_empty_datasets():
    """Defensively verifies HybridRiskEngine handles empty inputs without crashing."""
    context = PipelineContext(
        customer_features=pd.DataFrame(columns=["customer_id"]),
        rule_results=[],
        ml_results=[]
    )
    engine = HybridRiskEngine()
    results = engine.evaluate(context)
    assert len(results) == 0

def test_hybrid_risk_engine_duplicate_customer_ids(mock_pipeline_context):
    """Verifies that HybridRiskEngine skips duplicate rows defensively and logs a warning."""
    duped_df = pd.concat([mock_pipeline_context.customer_features.iloc[[0]], mock_pipeline_context.customer_features], ignore_index=True)
    
    context = PipelineContext(
        customer_features=duped_df,
        rule_results=mock_pipeline_context.rule_results,
        ml_results=mock_pipeline_context.ml_results
    )
    
    engine = HybridRiskEngine()
    results = engine.evaluate(context)
    assert len(results) == 3

def test_hybrid_risk_engine_missing_eval_results(mock_pipeline_context):
    """Verifies HybridRiskEngine works correctly when a customer lacks rule or ML results."""
    context = PipelineContext(
        customer_features=mock_pipeline_context.customer_features,
        rule_results=[],
        ml_results=mock_pipeline_context.ml_results
    )
    
    engine = HybridRiskEngine()
    results = engine.evaluate(context)
    
    assert len(results) == 3
    assert results[0].score_breakdown.rule_score == 0.0

# ====================================================
# INTEGRATION AND PERFORMANCE PERFORMANCE TESTS
# ====================================================

def test_pipeline_integration_runs_hybrid_risk(tmp_dir):
    """Verifies end-to-end pipeline execution executes the hybrid risk stage and populates results."""
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
    assert len(res.hybrid_risk_analysis) == 5
    assert isinstance(res.hybrid_risk_dataframe, pd.DataFrame)
    assert list(res.hybrid_risk_dataframe.columns) == [
        "customer_id", "overall_risk_score", "severity", "confidence",
        "rule_score", "ml_score", "behavioral_score", "recommendation",
        "explanation_summary", "triggered_rules_count"
    ]

def test_large_dataset_performance():
    """Validates that HybridRiskEngine runs within acceptable bounds on 10,000+ customer records."""
    customer_ids = [f"C_{i}" for i in range(10000)]
    features_df = pd.DataFrame({
        "customer_id": customer_ids,
        "velocity_score": np.random.uniform(0, 10, 10000),
        "structuring_score": np.random.uniform(0, 10, 10000),
        "cash_out_ratio": np.random.uniform(0, 1, 10000),
        "recipient_diversity": np.random.uniform(0, 15, 10000),
        "sender_diversity": np.random.uniform(0, 5, 10000)
    })
    
    rule_results = [AnalysisResult(customer_id=cid, total_rule_score=5, severity="LOW", triggered_rules=[]) for cid in customer_ids]
    ml_results = [AnalysisResult(customer_id=cid, severity="LOW", score=0.1, anomaly_score=0.1) for cid in customer_ids]
    
    context = PipelineContext(
        customer_features=features_df,
        rule_results=rule_results,
        ml_results=ml_results
    )
    
    engine = HybridRiskEngine()
    
    start_time = time.perf_counter()
    results = engine.evaluate(context)
    duration = time.perf_counter() - start_time
    
    assert len(results) == 10000
    # Performance benchmark: 10000 records evaluation must take less than 1.5 seconds
    assert duration < 1.5
