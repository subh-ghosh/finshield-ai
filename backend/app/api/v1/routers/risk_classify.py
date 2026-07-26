"""Risk Classification Router — converts ML/rule scores into risk categories."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
import numpy as np

router = APIRouter(prefix="/risk-classify", tags=["Risk Classification"])


def _safe(val):
    if isinstance(val, (np.bool_,)): return bool(val)
    if isinstance(val, np.integer): return int(val)
    if isinstance(val, np.floating): return float(val) if not np.isnan(val) else None
    return val


@router.get(
    "/{customer_id}",
    summary="Get Risk Classification for Customer",
    description=(
        "Returns the full risk classification for a customer: hybrid risk score (0-100), "
        "risk category (LOW/MEDIUM/HIGH/CRITICAL), severity, rule contributions, "
        "ML contributions, and recommended escalation action."
    )
)
def get_risk_classification(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns hybrid risk classification for a customer."""
    customer_id = customer_id.strip()
    hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
    h_res = hybrid_map.get(customer_id)

    if h_res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk classification for customer '{customer_id}' not found."
        )

    risk_score_pct = round(_safe(h_res.overall_risk_score) * 100, 2)

    # Map score to category
    if risk_score_pct < 35:
        category = "LOW"
    elif risk_score_pct < 65:
        category = "MEDIUM"
    elif risk_score_pct < 85:
        category = "HIGH"
    else:
        category = "CRITICAL"

    # Rule contributions
    rule_map = {res.customer_id: res for res in pipeline_res.rule_analysis}
    rule_res = rule_map.get(customer_id)
    rule_contribution = {
        "rule_score": _safe(rule_res.total_rule_score) if rule_res else 0,
        "triggered_rules": [str(r) for r in getattr(rule_res, "triggered_rules", [])] if rule_res else [],
        "rule_severity": str(rule_res.severity) if rule_res else "LOW",
    }

    # ML contribution
    anom_map = {res.customer_id: res for res in pipeline_res.anomaly_analysis}
    anom_res = anom_map.get(customer_id)
    ml_contribution = {
        "isolation_forest_score": round(_safe(anom_res.anomaly_score), 4) if anom_res else 0,
        "ml_severity": str(anom_res.severity) if anom_res else "LOW",
        "is_ml_flagged": (_safe(anom_res.anomaly_score) > 0.5) if anom_res else False,
    }

    return {
        "customer_id": customer_id,
        "risk_score_pct": risk_score_pct,
        "risk_category": category,
        "severity": str(h_res.severity),
        "recommendation": str(h_res.recommendation),
        "escalation_action": str(h_res.recommendation),
        "score_breakdown": {
            "overall_hybrid_score": _safe(h_res.overall_risk_score),
            "rule_weight": 0.3,
            "ml_weight": 0.3,
            "gnn_weight": 0.4,
        },
        "rule_contribution": rule_contribution,
        "ml_contribution": ml_contribution,
        "thresholds": {
            "LOW": "< 35",
            "MEDIUM": "35 - 65",
            "HIGH": "65 - 85",
            "CRITICAL": ">= 85"
        }
    }


@router.get(
    "/summary/distribution",
    summary="Risk Category Distribution",
    description="Returns the distribution of risk categories across all customers in the dataset."
)
def get_risk_distribution(
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns risk score distribution across all customers."""
    distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    high_risk = []

    for h_res in pipeline_res.hybrid_risk_analysis:
        score = _safe(h_res.overall_risk_score) * 100
        if score < 35:
            distribution["LOW"] += 1
        elif score < 65:
            distribution["MEDIUM"] += 1
        elif score < 85:
            distribution["HIGH"] += 1
        else:
            distribution["CRITICAL"] += 1
            high_risk.append({
                "customer_id": str(h_res.customer_id),
                "risk_score_pct": round(score, 1),
                "recommendation": str(h_res.recommendation),
            })

    total = len(pipeline_res.hybrid_risk_analysis)
    return {
        "total_customers": total,
        "distribution": distribution,
        "distribution_pct": {k: round(v / total * 100, 2) for k, v in distribution.items()} if total else {},
        "critical_customers": sorted(high_risk, key=lambda x: x["risk_score_pct"], reverse=True)[:20],
    }
