"""Feature Engineering Router — on-demand AML feature computation per customer."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
import numpy as np

router = APIRouter(prefix="/features", tags=["Feature Engineering"])


def _safe(val):
    if isinstance(val, (np.bool_,)): return bool(val)
    if isinstance(val, np.integer): return int(val)
    if isinstance(val, np.floating): return float(val) if not np.isnan(val) else None
    if isinstance(val, np.ndarray): return [_safe(v) for v in val.tolist()]
    return val


@router.get(
    "/{customer_id}",
    summary="Get AML Feature Vector for Customer",
    description=(
        "Returns the engineered AML feature vector for a single customer: "
        "transaction velocity, rolling sums, structuring score, smurfing score, "
        "cash-out ratio, amount deviation, and network risk."
    )
)
def get_customer_features(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns AML feature vector for a customer."""
    customer_id = customer_id.strip()
    feats = pipeline_res.customer_features
    match = feats[feats["customer_id"].astype(str) == customer_id]

    if len(match) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer '{customer_id}' not found in feature store."
        )

    row = {k: _safe(v) for k, v in match.iloc[0].to_dict().items()}

    # Structure the response with AML-relevant groupings
    aml_features = {
        "customer_id": customer_id,
        "velocity_features": {
            "transaction_count": row.get("transaction_count"),
            "rolling_count_24h": row.get("rolling_count_24h"),
            "days_since_last_transaction": row.get("days_since_last_transaction"),
            "velocity_score": row.get("velocity_score"),
        },
        "amount_features": {
            "total_amount": row.get("total_amount"),
            "average_amount": row.get("average_amount"),
            "rolling_amount_24h": row.get("rolling_amount_24h"),
            "amount_deviation": row.get("amount_deviation"),
            "cash_out_ratio": row.get("cash_out_ratio"),
        },
        "pattern_features": {
            "structuring_score": row.get("structuring_score"),
            "smurfing_score": row.get("smurfing_score"),
            "sequence_perplexity": row.get("sequence_perplexity"),
            "unique_receivers": row.get("unique_receivers"),
        },
        "network_features": {
            "network_risk": row.get("network_risk"),
            "gnn_risk_score": row.get("gnn_risk_score"),
        },
        "raw_features": row,
    }
    return aml_features
