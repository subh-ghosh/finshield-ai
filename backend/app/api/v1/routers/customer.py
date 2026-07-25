"""Customer router providing customer detail queries and direct explanation retrieval endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.dependencies import get_explainability_service, get_pipeline_result
from app.api.v1.schemas.responses import CustomerProfileResponse, ErrorResponse
from app.explainability.explainability_service import ExplainabilityService
from app.models.explainability_context import ExplainabilityContext
from app.models.evidence_bundle import EvidenceBundle
from app.models.explanation_response import ExplanationResponseV1
from app.models.pipeline_result import PipelineResult

router = APIRouter(tags=["Customer Management"])

@router.get(
    "/customer/{customer_id}",
    response_model=CustomerProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve customer feature profile and details",
    description="Fetches cached customer engineered feature metrics, rule summary, and anomaly score.",
    responses={
        404: {"model": ErrorResponse, "description": "Customer not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
def get_customer(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> CustomerProfileResponse:
    """Retrieves customer profile and feature metrics."""
    customer_id = customer_id.strip()
    
    features_df = pipeline_res.customer_features
    match_row = features_df[features_df["customer_id"].astype(str) == customer_id]
    
    if len(match_row) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID '{customer_id}' was not found in dataset."
        )

    feat_dict = match_row.iloc[0].to_dict()

    # Rule summary lookup
    rule_map = {res.customer_id: res for res in pipeline_res.rule_analysis}
    rule_res = rule_map.get(customer_id)
    rule_summary = {
        "score": rule_res.total_rule_score,
        "severity": rule_res.severity,
        "triggered_count": len(rule_res.triggered_rules)
    } if rule_res else None

    # Anomaly summary lookup
    anom_map = {res.customer_id: res for res in pipeline_res.anomaly_analysis}
    anom_res = anom_map.get(customer_id)
    anomaly_summary = {
        "anomaly_score": anom_res.anomaly_score,
        "severity": anom_res.severity,
        "confidence": anom_res.confidence
    } if anom_res else None

    return CustomerProfileResponse(
        customer_id=customer_id,
        feature_metrics=feat_dict,
        rule_summary=rule_summary,
        anomaly_summary=anomaly_summary
    )


@router.get(
    "/explanation/{customer_id}",
    response_model=ExplanationResponseV1,
    status_code=status.HTTP_200_OK,
    summary="Direct ExplanationResponseV1 report lookup",
    description="Returns ExplanationResponseV1 report for a customer ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Customer not found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
def get_explanation(
    customer_id: str,
    pipeline_res: PipelineResult = Depends(get_pipeline_result),
    explain_service: ExplainabilityService = Depends(get_explainability_service)
) -> ExplanationResponseV1:
    """Directly returns ExplanationResponseV1 for a customer."""
    customer_id = customer_id.strip()
    
    # Check if pre-compiled explanation report is cached
    for rep in pipeline_res.explainability_reports:
        if rep.customer_id == customer_id:
            return rep

    # If not in cache, compile dynamically
    hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
    h_res = hybrid_map.get(customer_id)
    
    if h_res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explanation report for customer ID '{customer_id}' was not found."
        )

    features_df = pipeline_res.customer_features
    match_row = features_df[features_df["customer_id"].astype(str) == customer_id]
    raw_feat = match_row.iloc[0].to_dict() if len(match_row) > 0 else {}

    exp_context = ExplainabilityContext(
        hybrid_result=h_res,
        evidence_bundle=EvidenceBundle(),
        pipeline_metadata={
            "raw_features": raw_feat,
            "dataset_name": pipeline_res.metadata.get("dataset_name", "transactions.csv")
        }
    )
    
    return explain_service.explain(exp_context)
