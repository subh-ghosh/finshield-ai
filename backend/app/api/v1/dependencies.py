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
        dataset_path = _resolve_dataset_path()
        logger.info(f"FastAPI Dependency: Running AMLPipeline on resolved dataset path: '{dataset_path}'...")
        _pipeline_result_cache = pipeline.run(dataset_path)
    return _pipeline_result_cache
