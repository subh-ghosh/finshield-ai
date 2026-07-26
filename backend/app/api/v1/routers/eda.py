"""EDA Router — Dataset-level Exploratory Data Analysis endpoint."""

from fastapi import APIRouter, Depends
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
import numpy as np

router = APIRouter(prefix="/eda", tags=["Exploratory Data Analysis"])


def _safe(val):
    """Convert numpy types to Python native."""
    if isinstance(val, (np.bool_,)): return bool(val)
    if isinstance(val, np.integer): return int(val)
    if isinstance(val, np.floating): return float(val) if not np.isnan(val) else None
    if isinstance(val, np.ndarray): return [_safe(v) for v in val.tolist()]
    return val


@router.get(
    "/summary",
    summary="Dataset EDA Summary",
    description=(
        "Returns an exploratory data analysis summary of the IBM AML transaction dataset: "
        "row counts, transaction type distribution, amount statistics, fraud rate, "
        "top risk customers, and feature baseline metrics."
    )
)
def get_eda_summary(
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> dict:
    """Returns dataset-level EDA summary for analyst review."""

    df = pipeline_res.clean_dataframe
    feats = pipeline_res.customer_features
    hybrid = pipeline_res.hybrid_risk_analysis

    # ── Transaction-level stats ──────────────────────────────────────────────
    total_tx = len(df)
    fraud_col = "is_fraud" if "is_fraud" in df.columns else None
    fraud_count = int(df[fraud_col].sum()) if fraud_col else 0
    fraud_rate = round(fraud_count / total_tx * 100, 4) if total_tx else 0

    tx_type_dist = {}
    if "transaction_type" in df.columns:
        tx_type_dist = {str(k): _safe(v) for k, v in df["transaction_type"].value_counts().head(10).items()}

    country_dist = {}
    if "country" in df.columns:
        country_dist = {str(k): _safe(v) for k, v in df["country"].value_counts().head(10).items()}

    amount_stats = {}
    if "amount" in df.columns:
        amount_stats = {
            "mean":   _safe(df["amount"].mean()),
            "median": _safe(df["amount"].median()),
            "std":    _safe(df["amount"].std()),
            "min":    _safe(df["amount"].min()),
            "max":    _safe(df["amount"].max()),
            "p95":    _safe(df["amount"].quantile(0.95)),
            "p99":    _safe(df["amount"].quantile(0.99)),
        }

    # ── Customer-level stats ─────────────────────────────────────────────────
    total_customers = len(feats)

    velocity_stats = {}
    if "transaction_count" in feats.columns:
        velocity_stats = {
            "mean_tx_count":   _safe(feats["transaction_count"].mean()),
            "max_tx_count":    _safe(feats["transaction_count"].max()),
            "p95_tx_count":    _safe(feats["transaction_count"].quantile(0.95)),
        }

    # ── Risk distribution from hybrid engine ────────────────────────────────
    risk_scores = [_safe(r.overall_risk_score * 100) for r in hybrid]
    risk_distribution = {
        "LOW (0-35)":       sum(1 for s in risk_scores if s < 35),
        "MEDIUM (35-65)":   sum(1 for s in risk_scores if 35 <= s < 65),
        "HIGH (65-85)":     sum(1 for s in risk_scores if 65 <= s < 85),
        "CRITICAL (85+)":   sum(1 for s in risk_scores if s >= 85),
    }

    # ── Top 10 riskiest customers ────────────────────────────────────────────
    top_risky = sorted(hybrid, key=lambda r: r.overall_risk_score, reverse=True)[:10]
    top_customers = [
        {
            "customer_id": str(r.customer_id),
            "risk_score":  round(_safe(r.overall_risk_score * 100), 1),
            "recommendation": str(r.recommendation),
            "severity": str(r.severity),
        }
        for r in top_risky
    ]

    # ── Anomaly baseline ────────────────────────────────────────────────────
    anomaly_df = pipeline_res.anomaly_dataframe
    anomaly_flagged = int((anomaly_df["prediction"] == -1).sum()) if "prediction" in anomaly_df.columns else 0
    rule_df = pipeline_res.rule_dataframe
    rule_flagged = int((rule_df["rule_score"] > 0).sum()) if "rule_score" in rule_df.columns else 0

    return {
        "dataset_summary": {
            "total_transactions": total_tx,
            "total_customers": total_customers,
            "fraud_transactions": fraud_count,
            "fraud_rate_pct": fraud_rate,
            "source": "IBM AML Simulation Dataset (Kaggle)",
        },
        "transaction_type_distribution": tx_type_dist,
        "country_distribution": country_dist,
        "amount_statistics_usd": amount_stats,
        "customer_velocity_baseline": velocity_stats,
        "risk_distribution": risk_distribution,
        "anomaly_detection": {
            "isolation_forest_flagged": anomaly_flagged,
            "rule_engine_flagged": rule_flagged,
        },
        "top_10_risky_customers": top_customers,
    }
