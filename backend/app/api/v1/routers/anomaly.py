"""Anomaly Detection Router — ML-based anomaly scoring per customer."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
import numpy as np

router = APIRouter(prefix="/anomaly", tags=["Anomaly Detection"])


def _safe(val):
    if isinstance(val, (np.bool_,)): return bool(val)
    if isinstance(val, np.integer): return int(val)
    if isinstance(val, np.floating): return float(val) if not np.isnan(val) else None
    if isinstance(val, np.ndarray): return [_safe(v) for v in val.tolist()]
    return val


@router.get(
    "/{customer_id}",
    summary="Get Anomaly Detection Score for Customer",
    description=(
        "Returns the Isolation Forest anomaly score, prediction, confidence, and severity "
        "for a single customer. Score of 1.0 = highly anomalous (suspicious). "
        "Prediction of -1 = flagged as outlier by ML model."
    )
)
def get_customer_anomaly(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns Isolation Forest anomaly result for a customer."""
    customer_id = customer_id.strip()
    anom_map = {res.customer_id: res for res in pipeline_res.anomaly_analysis}
    anom_res = anom_map.get(customer_id)

    if anom_res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Anomaly result for customer '{customer_id}' not found."
        )

    # Also pull anomaly_dataframe row for raw scores
    anom_df = pipeline_res.anomaly_dataframe
    df_row = anom_df[anom_df["customer_id"].astype(str) == customer_id]
    raw_scores = {k: _safe(v) for k, v in df_row.iloc[0].to_dict().items()} if len(df_row) > 0 else {}

    return {
        "customer_id": customer_id,
        "model": "Isolation Forest",
        "anomaly_score": _safe(anom_res.anomaly_score),
        "prediction": -1 if _safe(anom_res.anomaly_score) > 0.5 else 1,
        "severity": str(anom_res.severity),
        "confidence": _safe(anom_res.confidence),
        "is_anomaly": _safe(anom_res.anomaly_score) > 0.5,
        "interpretation": (
            "FLAGGED — customer exhibits statistically unusual transaction patterns "
            "consistent with money laundering behaviour."
            if _safe(anom_res.anomaly_score) > 0.5
            else "NORMAL — customer behaviour within expected statistical range."
        ),
        "triggered_patterns": [str(r) for r in getattr(anom_res, "triggered_rules", [])],
        "raw_ml_scores": raw_scores,
    }


@router.get(
    "/summary/top",
    summary="Top Anomalous Customers",
    description="Returns the top N customers ranked by Isolation Forest anomaly score."
)
def get_top_anomalous(
    top_n: int = 10,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns top N most anomalous customers."""
    sorted_results = sorted(
        pipeline_res.anomaly_analysis,
        key=lambda r: r.anomaly_score,
        reverse=True
    )[:top_n]

    return {
        "model": "Isolation Forest",
        "total_customers_scored": len(pipeline_res.anomaly_analysis),
        "total_anomalies_detected": sum(1 for r in pipeline_res.anomaly_analysis if r.anomaly_score > 0.5),
        "top_anomalous_customers": [
            {
                "customer_id": str(r.customer_id),
                "anomaly_score": round(_safe(r.anomaly_score), 4),
                "severity": str(r.severity),
                "confidence": round(_safe(r.confidence), 4),
            }
            for r in sorted_results
        ]
    }
