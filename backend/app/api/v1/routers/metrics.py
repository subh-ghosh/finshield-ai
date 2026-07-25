"""Metrics router providing pipeline profiling timings and ingestion stats."""

from fastapi import APIRouter, Depends, status
from app.api.v1.dependencies import get_pipeline_result
from app.api.v1.schemas.responses import MetricsResponse
from app.models.pipeline_result import PipelineResult

router = APIRouter(tags=["System Operations"])

@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Pipeline execution metrics and stage timings",
    description="Returns total ingested rows, engineered customer counts, flagged rules/anomalies, and stage profiling timings."
)
def get_metrics(
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> MetricsResponse:
    """Returns execution metrics and stage timings."""
    report = pipeline_res.report
    rule_df = pipeline_res.rule_dataframe
    anomaly_df = pipeline_res.anomaly_dataframe

    flagged_rules = int((rule_df["rule_score"] > 0).sum()) if "rule_score" in rule_df.columns else 0
    flagged_anoms = int((anomaly_df["prediction"] == -1).sum()) if "prediction" in anomaly_df.columns else 0
    
    timings_dict = pipeline_res.metadata.get("timings", {})

    return MetricsResponse(
        total_rows=report.total_rows,
        clean_rows=report.clean_rows,
        engineered_customers=len(pipeline_res.customer_features),
        flagged_rules_count=flagged_rules,
        flagged_anomalies_count=flagged_anoms,
        execution_time_seconds=round(pipeline_res.execution_time, 4),
        timings={k: round(v, 4) for k, v in timings_dict.items()}
    )
