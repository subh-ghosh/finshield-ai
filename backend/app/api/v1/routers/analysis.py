"""Analysis router providing single customer and batch risk analysis endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import numpy as np
from app.api.v1.dependencies import get_explainability_service, get_pipeline_result
from app.api.v1.schemas.requests import CustomerAnalysisRequest, BatchAnalysisRequest
from app.api.v1.schemas.responses import ErrorResponse
from app.explainability.explainability_service import ExplainabilityService
from app.models.explainability_context import ExplainabilityContext
from app.models.evidence_bundle import EvidenceBundle
from app.models.explanation_response import ExplanationResponseV1
from app.models.pipeline_result import PipelineResult

def _convert_numpy_types(obj):
    if isinstance(obj, dict):
        return {k: _convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return _convert_numpy_types(obj.tolist())
    return obj

router = APIRouter(prefix="/analyze", tags=["Risk Analysis"])

@router.post(
    "/customer",
    response_model=ExplanationResponseV1,
    status_code=status.HTTP_200_OK,
    summary="Analyze single customer profile",
    description="Evaluates a single customer ID across Rule Engine, Isolation Forest, and Behavioral modules to return a versioned ExplanationResponseV1 report.",
    responses={
        404: {"model": ErrorResponse, "description": "Customer ID not found"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
def analyze_customer(
    request: CustomerAnalysisRequest,
    pipeline_res: PipelineResult = Depends(get_pipeline_result),
    explain_service: ExplainabilityService = Depends(get_explainability_service)
) -> ExplanationResponseV1:
    """Analyzes a single customer profile."""
    customer_id = request.customer_id
    
    # Locate hybrid risk evaluation result
    hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
    h_res = hybrid_map.get(customer_id)
    
    if h_res is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID '{customer_id}' was not found in active dataset evaluation results."
        )

    # Locate raw feature record
    features_df = pipeline_res.customer_features
    match_row = features_df[features_df["customer_id"].astype(str) == customer_id]
    raw_feat = _convert_numpy_types(match_row.iloc[0].to_dict() if len(match_row) > 0 else {})

    exp_context = ExplainabilityContext(
        hybrid_result=h_res,
        evidence_bundle=EvidenceBundle(),
        pipeline_metadata={
            "raw_features": raw_feat,
            "dataset_name": pipeline_res.metadata.get("dataset_name", "transactions.csv")
        }
    )
    
    return explain_service.explain(exp_context)


@router.post(
    "/batch",
    response_model=List[ExplanationResponseV1],
    status_code=status.HTTP_200_OK,
    summary="Analyze batch of customer profiles",
    description="Evaluates multiple customer IDs in a single request and returns a list of ExplanationResponseV1 reports.",
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request / Empty Batch"},
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
def analyze_batch(
    request: BatchAnalysisRequest,
    pipeline_res: PipelineResult = Depends(get_pipeline_result),
    explain_service: ExplainabilityService = Depends(get_explainability_service)
) -> List[ExplanationResponseV1]:
    """Analyzes a batch of customer profiles."""
    customer_ids = request.customer_ids
    
    hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
    features_df = pipeline_res.customer_features
    features_dict_map = {str(r["customer_id"]): r for r in features_df.to_dict(orient="records")}
    
    reports: List[ExplanationResponseV1] = []
    missing_ids: List[str] = []

    for cid in customer_ids:
        h_res = hybrid_map.get(cid)
        if h_res is None:
            missing_ids.append(cid)
            continue
            
        raw_feat = _convert_numpy_types(features_dict_map.get(cid, {}))
        exp_context = ExplainabilityContext(
            hybrid_result=h_res,
            evidence_bundle=EvidenceBundle(),
            pipeline_metadata={
                "raw_features": raw_feat,
                "dataset_name": pipeline_res.metadata.get("dataset_name", "transactions.csv")
            }
        )
        reports.append(explain_service.explain(exp_context))

    if not reports and missing_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"None of the requested customer IDs were found in dataset. Missing IDs: {missing_ids[:5]}"
        )

    return reports
