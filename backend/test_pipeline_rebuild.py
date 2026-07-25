"""
Test the full pipeline rebuild from cached pickle - standalone test.
Run this to validate all method names before wiring into dependencies.py
"""
import sys
import os
sys.path.insert(0, os.getcwd())

import pickle
import glob

print("=== Finding cached pickle ===")
pkl_files = glob.glob("data/cache/*.pkl")
print(f"Found: {pkl_files}")

pkl_path = pkl_files[0]
print(f"\n=== Loading pickle from {pkl_path} ===")
with open(pkl_path, "rb") as f:
    cached_df = pickle.load(f)
print(f"Loaded DataFrame: {len(cached_df)} rows, columns: {list(cached_df.columns[:5])}...")

print("\n=== Feature Engineering ===")
from app.services.feature_engineering import FeatureEngineering
fe = FeatureEngineering()
customer_features = fe.run(cached_df)
print(f"Customer features: {len(customer_features)} rows, columns: {list(customer_features.columns[:5])}...")

print("\n=== Rule Engine ===")
from app.services.rule_engine import RuleEngine
rule_engine = RuleEngine()
rule_analysis = rule_engine.run(customer_features)
print(f"Rule analysis: {len(rule_analysis)} results")
rule_df = RuleEngine.to_dataframe(rule_analysis)
print(f"Rule df shape: {rule_df.shape}")

print("\n=== Anomaly Detection ===")
from app.ml.anomaly_detection import AnomalyDetection
detector = AnomalyDetection()
anomaly_analysis = detector.run(customer_features)
print(f"Anomaly analysis: {len(anomaly_analysis)} results")

print("\n=== Hybrid Risk Engine ===")
from app.ml.hybrid_risk_engine import HybridRiskEngine
from app.models.pipeline_context import PipelineContext
eval_context = PipelineContext(
    customer_features=customer_features,
    rule_results=rule_analysis,
    ml_results=anomaly_analysis,
    pipeline_version="2.0.0-cached",
    dataset_info={"name": "transactions.csv (cached)", "hash": "cached"}
)
hybrid_engine = HybridRiskEngine()
hybrid_analysis = hybrid_engine.evaluate(eval_context)
print(f"Hybrid analysis: {len(hybrid_analysis)} results")
hybrid_df = HybridRiskEngine.to_dataframe(hybrid_analysis)
print(f"Hybrid df shape: {hybrid_df.shape}")

print("\n=== PipelineResult ===")
from app.services.preprocessing import PreprocessingReport
from app.models.pipeline_result import PipelineResult
import pandas as pd

report = PreprocessingReport(
    total_rows=len(cached_df), clean_rows=len(cached_df),
    missing_percentage=0.0, duplicate_percentage=0.0, invalid_percentage=0.0,
    null_columns=[], completeness_score=1.0,
    execution_time=0.0, columns_normalized=[],
    schema_mappings={}, warnings=[], data_quality_score=1.0
)
result = PipelineResult(
    clean_dataframe=cached_df,
    customer_features=customer_features,
    rule_analysis=rule_analysis,
    rule_dataframe=rule_df,
    anomaly_analysis=anomaly_analysis,
    anomaly_dataframe=pd.DataFrame(),
    hybrid_risk_analysis=hybrid_analysis,
    hybrid_risk_dataframe=hybrid_df,
    report=report,
    execution_time=0.0,
    pipeline_version="2.0.0-cached",
    model_versions={"isolation_forest": "1.0", "rule_engine": "1.0", "hybrid_risk_engine": "1.0"},
    metadata={"dataset_name": "cached", "dataset_hash": "cached"}
)
print(f"PipelineResult created successfully!")
print(f"  Customers: {len(result.customer_features)}")
print(f"  Hybrid results: {len(result.hybrid_risk_analysis)}")

# Test a specific customer lookup
print("\n=== Customer Lookup Test (CUST-8392) ===")
features_df = result.customer_features
match = features_df[features_df["customer_id"].astype(str) == "CUST-8392"]
if match.empty:
    # Try partial match
    all_ids = features_df["customer_id"].astype(str).tolist()
    print(f"CUST-8392 not found. Sample IDs: {all_ids[:10]}")
else:
    print(f"Found CUST-8392! Data: {match.iloc[0].to_dict()}")

print("\n=== ALL PIPELINE STAGES PASSED ===")
