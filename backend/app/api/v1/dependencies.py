"""FastAPI dependency injection providers for services, pipeline instances, and caches."""

import os
import time
from typing import Optional
from app.config import PipelineConfig
from app.services.pipeline import AMLPipeline
from app.explainability.explainability_service import ExplainabilityService
from app.models.pipeline_result import PipelineResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Start timestamp for uptime metrics calculation
APP_START_TIME: float = time.time()

# Cached pipeline instance singleton
_pipeline_instance: Optional[AMLPipeline] = None
_pipeline_result_cache: Optional[PipelineResult] = None
_explainability_service_instance: Optional[ExplainabilityService] = None

def get_pipeline() -> AMLPipeline:
    """FastAPI Dependency providing AMLPipeline instance.

    Returns:
        AMLPipeline: Initialized AMLPipeline instance.
    """
    global _pipeline_instance
    if _pipeline_instance is None:
        config = PipelineConfig(
            remove_duplicates=True,
            validate_amounts=True,
            save_rejected_rows=True,
            generate_metadata=True,
            generate_report=True,
            sort_records=True,
            use_cache=True,
            reports_dir="reports",
            rejected_dir="reports/rejected",
            cache_dir=".cache",
            feature_store_dir=".feature_store"
        )
        _pipeline_instance = AMLPipeline(config)
        logger.info("FastAPI Dependency: Initialized AMLPipeline singleton.")
    return _pipeline_instance

def get_explainability_service() -> ExplainabilityService:
    """FastAPI Dependency providing ExplainabilityService instance.

    Returns:
        ExplainabilityService: Initialized ExplainabilityService instance.
    """
    global _explainability_service_instance
    if _explainability_service_instance is None:
        _explainability_service_instance = ExplainabilityService()
        logger.info("FastAPI Dependency: Initialized ExplainabilityService singleton.")
    return _explainability_service_instance

def _resolve_dataset_path() -> str:
    """Resolves dataset filepath across execution paths.

    Returns:
        str: Absolute or relative filepath.
    """
    candidate_paths = [
        "IBM AML Transaction Dataset (IBM AMLSim)/transactions.csv",
        "../IBM AML Transaction Dataset (IBM AMLSim)/transactions.csv",
        "../../IBM AML Transaction Dataset (IBM AMLSim)/transactions.csv",
        "/home/arhit/Desktop/Socite General Hackathon/IBM AML Transaction Dataset (IBM AMLSim)/transactions.csv"
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    # Fallback default
    return candidate_paths[0]

def get_pipeline_result() -> PipelineResult:
    """FastAPI Dependency providing executed PipelineResult context.

    Returns:
        PipelineResult: Pipeline execution result.
    """
    global _pipeline_result_cache
    if _pipeline_result_cache is None:
        pipeline = get_pipeline()
        
        # Check if running in production with database configured
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            logger.info("DATABASE_URL detected. Dumping transactions from PostgreSQL...")
            try:
                import pandas as pd
                from sqlalchemy import create_engine
                engine = create_engine(db_url)
                df = pd.read_sql("SELECT * FROM transactions", engine)
                
                # Save to temp csv for pipeline
                temp_csv = os.path.join(pipeline.config.cache_dir, "postgres_dump.csv")
                os.makedirs(pipeline.config.cache_dir, exist_ok=True)
                df.to_csv(temp_csv, index=False)
                logger.info(f"Successfully dumped PostgreSQL data to {temp_csv}. Running pipeline...")
                _pipeline_result_cache = pipeline.run(temp_csv)
                return _pipeline_result_cache
            except Exception as e:
                logger.error(f"Failed to load from PostgreSQL, falling back to local files: {e}")

        dataset_path = _resolve_dataset_path()

        if not os.path.exists(dataset_path):
            # Dataset CSV not present — attempt to load from cached pickle
            logger.warning(f"Dataset file not found at '{dataset_path}'. Attempting to load from cache...")
            import pickle
            import glob
            # __file__ = backend/app/api/v1/dependencies.py → 4x dirname = backend/
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            cache_dir = pipeline.config.cache_dir if hasattr(pipeline, 'config') else "data/cache"
            cache_dirs = [
                os.path.join(base_dir, "data", "cache"),
                os.path.join(base_dir, ".cache"),
                os.path.join(base_dir, "reports"),
            ]
            for cdir in cache_dirs:
                logger.info(f"Checking cache dir: '{cdir}' (exists: {os.path.exists(cdir)})")
                pkl_files = glob.glob(os.path.join(cdir, "*.pkl"))
                if pkl_files:
                    pkl_path = pkl_files[0]
                    logger.info(f"Found cached pickle at '{pkl_path}'. Loading...")
                    try:
                        with open(pkl_path, "rb") as f:
                            cached_df = pickle.load(f)
                        # Run full pipeline stages from cached clean DataFrame
                        from app.services.feature_engineering import FeatureEngineering
                        from app.services.rule_engine import RuleEngine
                        from app.ml.anomaly_detection import AnomalyDetection
                        from app.ml.hybrid_risk_engine import HybridRiskEngine
                        from app.models.pipeline_context import PipelineContext
                        from app.services.preprocessing import PreprocessingReport
                        import pandas as pd

                        fe = FeatureEngineering()
                        customer_features = fe.run(cached_df)

                        rule_engine = RuleEngine()
                        rule_analysis = rule_engine.run(customer_features)
                        rule_df = RuleEngine.to_dataframe(rule_analysis)

                        detector = AnomalyDetection()
                        anomaly_analysis = detector.run(customer_features)
                        anomaly_df = AnomalyDetection.to_dataframe(anomaly_analysis)

                        eval_context = PipelineContext(
                            customer_features=customer_features,
                            rule_results=rule_analysis,
                            ml_results=anomaly_analysis,
                            pipeline_version="2.0.0-cached",
                            dataset_info={"name": "transactions.csv (cached)", "hash": "cached"}
                        )
                        hybrid_engine = HybridRiskEngine()
                        hybrid_analysis = hybrid_engine.evaluate(eval_context)
                        hybrid_df = HybridRiskEngine.to_dataframe(hybrid_analysis)

                        report = PreprocessingReport(
                            total_rows=len(cached_df), clean_rows=len(cached_df),
                            missing_percentage=0.0, duplicate_percentage=0.0, invalid_percentage=0.0,
                            null_columns=[], completeness_score=1.0,
                            execution_time=0.0, columns_normalized=[],
                            schema_mappings={}, warnings=[], data_quality_score=1.0
                        )

                        _pipeline_result_cache = PipelineResult(
                            clean_dataframe=cached_df,
                            customer_features=customer_features,
                            rule_analysis=rule_analysis,
                            rule_dataframe=rule_df,
                            anomaly_analysis=anomaly_analysis,
                            anomaly_dataframe=anomaly_df,
                            hybrid_risk_analysis=hybrid_analysis,
                            hybrid_risk_dataframe=hybrid_df,
                            report=report,
                            execution_time=0.0,
                            pipeline_version="2.0.0-cached",
                            model_versions={"isolation_forest": "1.0", "rule_engine": "1.0", "hybrid_risk_engine": "1.0"},
                            metadata={"dataset_name": "transactions.csv (cached)", "dataset_hash": "cached"}
                        )
                        logger.info("Pipeline result built from cached dataset successfully.")
                        return _pipeline_result_cache
                    except Exception as e:
                        logger.error(f"Failed to load cached pickle: {e}", exc_info=True)
                        continue
            raise FileNotFoundError(
                f"Dataset not found at '{dataset_path}' and no valid cache exists. "
                "Please place the transactions.csv file in the expected directory."
            )

        logger.info(f"FastAPI Dependency: Running AMLPipeline on resolved dataset path: '{dataset_path}'...")
        _pipeline_result_cache = pipeline.run(dataset_path)
    return _pipeline_result_cache
