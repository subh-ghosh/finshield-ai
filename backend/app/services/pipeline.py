"""Pipeline orchestrator coordinating ingestion, preprocessing, features, and model runs."""

from dataclasses import dataclass
import os
import time
from typing import Optional
import pandas as pd
from app.config import PIPELINE_VERSION, PipelineConfig
from app.config import ml_config
from app.contracts.data_contract import DataContractValidator
from app.ml.anomaly_detection import AnomalyDetection
from app.ml.confidence_calculator import ConfidenceCalculator
from app.ml.feature_selector import FeatureSelector
from app.ml.model_registry import ModelRegistry
from app.ml.hybrid_risk_engine import HybridRiskEngine
from app.explainability.explainability_service import ExplainabilityService
from app.models.explainability_context import ExplainabilityContext
from app.models.evidence_bundle import EvidenceBundle
from app.models.pipeline_context import PipelineContext
from app.models.pipeline_result import PipelineResult
from app.services.cache_manager import CacheManager
from app.services.feature_engineering import FeatureEngineering
from app.services.feature_store import FeatureStore
from app.services.preprocessing import AMLPreprocessor, PreprocessingReport
from app.services.rule_engine import RuleEngine
from app.utils.logger import get_logger
from app.utils.pipeline_events import PipelineEvents
from app.utils.pipeline_profiler import PipelineProfiler
from app.utils.timer import reset_timings, time_stage

logger = get_logger(__name__)

@dataclass
class PipelineRunContext:
    """Lightweight metadata class tracking the state of a single pipeline run."""
    dataset_name: str
    dataset_hash: str
    pipeline_version: str
    start_time: float
    execution_time: float = 0.0
    configuration: Optional[PipelineConfig] = None


class AMLPipeline:
    """Orchestrates data loading, cleaning, validation, feature engineering, and ML model evaluations."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initializes the preprocessing and detection pipeline.

        Args:
            config: Optional PipelineConfig override settings.
        """
        self.config = config or PipelineConfig()
        self.preprocessor = AMLPreprocessor()
        self.feature_store = FeatureStore(self.config.feature_store_dir)
        self.context: Optional[PipelineRunContext] = None

    @time_stage("Total Pipeline Run")
    def run(self, filepath: str) -> PipelineResult:
        """Runs the ingestion, preprocessing, validation, feature engineering, rules, and anomalies.

        Args:
            filepath: Path to raw transactions CSV.

        Returns:
            PipelineResult: Consolidated result dataclass.
        """
        # Reset local timing metrics and profiler
        reset_timings()
        PipelineProfiler.reset()
        start_time = time.perf_counter()
        
        # Calculate dataset identifiers
        dataset_name = os.path.basename(filepath)
        dataset_hash = CacheManager.calculate_file_hash(filepath)
        
        # Dispatch event PipelineStarted
        PipelineEvents.on_pipeline_started(dataset_name)
        
        # Build Context
        self.context = PipelineRunContext(
            dataset_name=dataset_name,
            dataset_hash=dataset_hash,
            pipeline_version=PIPELINE_VERSION,
            start_time=start_time,
            configuration=self.config
        )

        logger.info(f"Pipeline Started - Version: {PIPELINE_VERSION} - Dataset: {dataset_name} ({dataset_hash})")

        # 1. Cache Check
        if self.config.use_cache:
            cached_df = CacheManager.load_cached_dataset(dataset_hash, self.config.cache_dir)
            if cached_df is not None:
                # Restore preprocessor properties to enable reporting
                self.preprocessor.rows_loaded = len(cached_df)
                self.preprocessor.clean_df = cached_df
                # Setup empty rejected logs for cache hit
                self.preprocessor.duplicate_df = pd.DataFrame(columns=cached_df.columns)
                self.preprocessor.invalid_df = pd.DataFrame(columns=cached_df.columns)
                self.preprocessor.missing_df = pd.DataFrame(columns=cached_df.columns)
                
                # Check data contract
                with PipelineProfiler.profile("Validation"):
                    DataContractValidator.validate(cached_df)
                
                # Run Feature Engineering
                with PipelineProfiler.profile("Feature Engineering"):
                    fe = FeatureEngineering()
                    customer_features = fe.run(cached_df)
                
                PipelineEvents.on_feature_engineering_completed(len(customer_features))
                
                # Save customer features to Feature Store
                self.feature_store.save(customer_features)
                
                # Run Rule Engine
                with PipelineProfiler.profile("Rule Engine"):
                    rule_engine = RuleEngine()
                    rule_analysis = rule_engine.run(customer_features)
                    rule_df = rule_engine.to_dataframe(rule_analysis)
                
                flagged_rules_count = int((rule_df["rule_score"] > 0).sum())
                PipelineEvents.on_rule_engine_completed(flagged_rules_count)
                
                # Run Anomaly Detection with dependency injection
                with PipelineProfiler.profile("Isolation Forest"):
                    selector = FeatureSelector(ml_config.FEATURE_COLUMNS)
                    calculator = ConfidenceCalculator()
                    registry = ModelRegistry()
                    
                    anomaly_engine = AnomalyDetection(
                        feature_selector=selector,
                        config=ml_config,
                        model_registry=registry,
                        confidence_calculator=calculator
                    )
                    anomaly_analysis = anomaly_engine.run(customer_features)
                    anomaly_df = anomaly_engine.to_dataframe(anomaly_analysis)
                
                flagged_anoms_count = int((anomaly_df["prediction"] == -1).sum())
                PipelineEvents.on_anomaly_detection_completed(flagged_anoms_count)
                
                # Run Hybrid Risk Engine
                with PipelineProfiler.profile("Hybrid Risk"):
                    eval_context = PipelineContext(
                        customer_features=customer_features,
                        rule_results=rule_analysis,
                        ml_results=anomaly_analysis,
                        pipeline_version=PIPELINE_VERSION,
                        dataset_info={"name": dataset_name, "hash": dataset_hash}
                    )
                    hybrid_engine = HybridRiskEngine()
                    hybrid_analysis = hybrid_engine.evaluate(eval_context)
                    hybrid_df = HybridRiskEngine.to_dataframe(hybrid_analysis)

                # Run Explainability Service (optimized execution loop)
                with PipelineProfiler.profile("Explainability Report"):
                    explain_service = ExplainabilityService()
                    explain_reports = []
                    features_dict_map = {str(r["customer_id"]): r for r in customer_features.to_dict(orient="records")}
                    for h_res in hybrid_analysis:
                        raw_feat = features_dict_map.get(h_res.customer_id, {})
                        exp_context = ExplainabilityContext(
                            hybrid_result=h_res,
                            evidence_bundle=EvidenceBundle(),
                            pipeline_metadata={"raw_features": raw_feat, "dataset_name": dataset_name}
                        )
                        explain_reports.append(explain_service.explain(exp_context))
                
                elapsed = time.perf_counter() - start_time
                self.context.execution_time = elapsed
                report = self.preprocessor.generate_report(elapsed)
                
                PipelineEvents.on_pipeline_finished(elapsed)
                
                logger.info("Pipeline Completed (via Cache Hit)")
                return PipelineResult(
                    clean_dataframe=cached_df,
                    customer_features=customer_features,
                    rule_analysis=rule_analysis,
                    rule_dataframe=rule_df,
                    anomaly_analysis=anomaly_analysis,
                    anomaly_dataframe=anomaly_df,
                    hybrid_risk_analysis=hybrid_analysis,
                    hybrid_risk_dataframe=hybrid_df,
                    explainability_reports=explain_reports,
                    report=report,
                    execution_time=elapsed,
                    pipeline_version=PIPELINE_VERSION,
                    model_versions={"isolation_forest": "1.0", "rule_engine": "1.0", "hybrid_risk_engine": "1.0", "explainability_service": "1.0"},
                    metadata={
                        "dataset_name": dataset_name,
                        "dataset_hash": dataset_hash,
                        "timings": PipelineProfiler.get_profile_timings()
                    }
                )

        # 2. Ingestion
        with PipelineProfiler.profile("Dataset Loader"):
            df = self._load(filepath)
        
        # 3. Column Normalization
        with PipelineProfiler.profile("Schema Mapper"):
            df = self._normalize(df)
            df = self._map_schema(df)
        
        # 5. Schema Validation
        with PipelineProfiler.profile("Validation"):
            self._validate_schema(df)
        
        # 6. Preprocessing (cleaning, types, sorting, duplicates)
        with PipelineProfiler.profile("Preprocessing"):
            df = self._convert_dtypes(df)
            df = self._clean_missing_values(df)
            if self.config.remove_duplicates:
                df = self._remove_duplicates(df)
            else:
                self.preprocessor.duplicate_df = pd.DataFrame(columns=df.columns)
                
            if self.config.validate_amounts:
                df = self._validate_amounts(df)
            else:
                self.preprocessor.invalid_df = pd.DataFrame(columns=df.columns)
                
            if self.config.sort_records:
                df = self._sort(df)
            
        self.preprocessor.clean_df = df

        # Strict validation of data contract before boundary exit
        with PipelineProfiler.profile("Validation"):
            DataContractValidator.validate(df)

        # 11. Save Audit Reports
        if self.config.save_rejected_rows:
            self._save_audit_reports()

        # Compute elapsed time
        elapsed = time.perf_counter() - start_time
        self.context.execution_time = elapsed
        
        # 12. Preprocessing Report & Metadata
        report = self.preprocessor.generate_report(elapsed)
        
        if self.config.generate_metadata:
            meta_path = os.path.join(self.config.reports_dir, "metadata.json")
            self.preprocessor.save_metadata(meta_path, elapsed)
            
            profile_path = os.path.join(self.config.reports_dir, "dataset_profile.json")
            self.preprocessor.generate_profile(profile_path)
            
            logger.info("Metadata Generated")

        # 13. Cache Save (of clean transactions dataframe)
        if self.config.use_cache:
            CacheManager.save_to_cache(df, dataset_hash, self.config.cache_dir)

        # 14. Feature Engineering
        with PipelineProfiler.profile("Feature Engineering"):
            fe = FeatureEngineering()
            customer_features = fe.run(df)

        PipelineEvents.on_feature_engineering_completed(len(customer_features))

        # 15. Save customer-level features to Feature Store
        self.feature_store.save(customer_features)

        # 16. Run Rule Engine
        with PipelineProfiler.profile("Rule Engine"):
            rule_engine = RuleEngine()
            rule_analysis = rule_engine.run(customer_features)
            rule_df = rule_engine.to_dataframe(rule_analysis)

        flagged_rules_count = int((rule_df["rule_score"] > 0).sum())
        PipelineEvents.on_rule_engine_completed(flagged_rules_count)

        # 17. Run Anomaly Detection with dependency injection
        with PipelineProfiler.profile("Isolation Forest"):
            selector = FeatureSelector(ml_config.FEATURE_COLUMNS)
            calculator = ConfidenceCalculator()
            registry = ModelRegistry()
            
            anomaly_engine = AnomalyDetection(
                feature_selector=selector,
                config=ml_config,
                model_registry=registry,
                confidence_calculator=calculator
            )
            anomaly_analysis = anomaly_engine.run(customer_features)
            anomaly_df = anomaly_engine.to_dataframe(anomaly_analysis)

        flagged_anoms_count = int((anomaly_df["prediction"] == -1).sum())
        PipelineEvents.on_anomaly_detection_completed(flagged_anoms_count)

        # 18. Run Hybrid Risk Engine
        with PipelineProfiler.profile("Hybrid Risk"):
            eval_context = PipelineContext(
                customer_features=customer_features,
                rule_results=rule_analysis,
                ml_results=anomaly_analysis,
                pipeline_version=PIPELINE_VERSION,
                dataset_info={"name": dataset_name, "hash": dataset_hash}
            )
            hybrid_engine = HybridRiskEngine()
            hybrid_analysis = hybrid_engine.evaluate(eval_context)
            hybrid_df = HybridRiskEngine.to_dataframe(hybrid_analysis)

        # 19. Run Explainability Service
        with PipelineProfiler.profile("Explainability Report"):
            explain_service = ExplainabilityService()
            explain_reports = []
            features_dict_map = {str(r["customer_id"]): r for r in customer_features.to_dict(orient="records")}
            for h_res in hybrid_analysis:
                raw_feat = features_dict_map.get(h_res.customer_id, {})
                exp_context = ExplainabilityContext(
                    hybrid_result=h_res,
                    evidence_bundle=EvidenceBundle(),
                    pipeline_metadata={"raw_features": raw_feat, "dataset_name": dataset_name}
                )
                explain_reports.append(explain_service.explain(exp_context))

        # 11. 2026-Era Federated Learning Simulation
        try:
            from app.federated.local_trainer import FederatedLocalTrainer
            fl_trainer = FederatedLocalTrainer(export_dir=self.config.reports_dir)
            fl_trainer.export_dp_weights(dataset_hash, anomaly_engine)
            # Federated export completed
        except Exception as e:
            logger.warning(f"Federated learning export failed (non-critical): {e}")

        logger.info("Pipeline Completed")
        
        PipelineEvents.on_pipeline_finished(elapsed)
        
        return PipelineResult(
            clean_dataframe=df,
            customer_features=customer_features,
            rule_analysis=rule_analysis,
            rule_dataframe=rule_df,
            anomaly_analysis=anomaly_analysis,
            anomaly_dataframe=anomaly_df,
            hybrid_risk_analysis=hybrid_analysis,
            hybrid_risk_dataframe=hybrid_df,
            explainability_reports=explain_reports,
            report=report,
            execution_time=elapsed,
            pipeline_version=PIPELINE_VERSION,
            model_versions={"isolation_forest": "1.0", "rule_engine": "1.0", "hybrid_risk_engine": "1.0", "explainability_service": "1.0"},
            metadata={
                "dataset_name": dataset_name,
                "dataset_hash": dataset_hash,
                "timings": PipelineProfiler.get_profile_timings()
            }
        )

    @time_stage("Loading")
    def _load(self, filepath: str) -> pd.DataFrame:
        df = self.preprocessor.load_data(filepath)
        logger.info("Dataset Loaded")
        return df

    @time_stage("Normalization")
    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.preprocessor.normalize_column_names(df)

    @time_stage("Schema Mapping")
    def _map_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.preprocessor.map_schema(df)
        logger.info("Schema Mapping Complete")
        return df

    def _validate_schema(self, df: pd.DataFrame) -> None:
        self.preprocessor.validate_schema(df)

    @time_stage("Type Conversion")
    def _convert_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.preprocessor.convert_dtypes(df)

    @time_stage("Cleaning")
    def _clean_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.preprocessor.clean_missing_values(df)
        logger.info("Cleaning Complete")
        return df

    @time_stage("Duplicate Removal")
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.preprocessor.remove_duplicates(df)

    @time_stage("Validation")
    def _validate_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.preprocessor.validate_amounts(df)
        logger.info("Validation Complete")
        return df

    @time_stage("Sorting")
    def _sort(self, df: pd.DataFrame) -> pd.DataFrame:
        return self.preprocessor.sort_by_timestamp(df)

    @time_stage("Saving Audit")
    def _save_audit_reports(self) -> None:
        rejected_dir = self.config.rejected_dir
        os.makedirs(rejected_dir, exist_ok=True)
        
        dup_path = os.path.join(rejected_dir, "duplicate_rows.csv")
        self._write_df(self.preprocessor.duplicate_df, dup_path)
            
        inv_path = os.path.join(rejected_dir, "invalid_rows.csv")
        self._write_df(self.preprocessor.invalid_df, inv_path)
            
        miss_path = os.path.join(rejected_dir, "missing_rows.csv")
        self._write_df(self.preprocessor.missing_df, miss_path)

    @staticmethod
    def _write_df(df: Optional[pd.DataFrame], path: str) -> None:
        if df is not None:
            df.to_csv(path, index=False)
        else:
            pd.DataFrame().to_csv(path, index=False)
