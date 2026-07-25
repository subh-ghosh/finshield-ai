"""Pipeline lifecycle events logging class."""

from app.utils.logger import get_logger

logger = get_logger(__name__)

class PipelineEvents:
    """Lightweight event dispatcher that writes structured execution state changes to the logs."""

    @staticmethod
    def on_pipeline_started(dataset_name: str) -> None:
        """Invoked when pipeline starts processing a dataset."""
        logger.info(f"[EVENT: PipelineStarted] Ingesting dataset: {dataset_name}")

    @staticmethod
    def on_feature_engineering_completed(features_count: int) -> None:
        """Invoked when Feature Engineering completes."""
        logger.info(f"[EVENT: FeatureEngineeringCompleted] Engineered profiles for {features_count} customers")

    @staticmethod
    def on_rule_engine_completed(flagged_count: int) -> None:
        """Invoked when Rule Engine completes."""
        logger.info(f"[EVENT: RuleEngineCompleted] Flagged {flagged_count} customers via rule violations")

    @staticmethod
    def on_anomaly_detection_completed(flagged_count: int) -> None:
        """Invoked when Isolation Forest completes."""
        logger.info(f"[EVENT: AnomalyDetectionCompleted] Identified {flagged_count} customer anomalies")

    @staticmethod
    def on_pipeline_finished(execution_time: float) -> None:
        """Invoked when the entire pipeline run finishes."""
        logger.info(f"[EVENT: PipelineFinished] Completed total execution in {execution_time:.4f}s")
