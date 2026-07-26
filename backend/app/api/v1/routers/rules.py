"""REST API Router for AI-driven Rule Suggestions."""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.v1.schemas.responses import ApiResponse
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult
from app.rules.rule_suggestion_engine import RuleSuggestionEngine, RuleSuggestion
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Rule Suggestions"])

# Singleton engine instance
_engine = RuleSuggestionEngine()


def _get_anomaly_scores(pipeline_result: PipelineResult) -> dict:
    """Extract anomaly scores from pipeline result for rule analysis."""
    scores = {}
    if hasattr(pipeline_result, "hybrid_risk_analysis") and pipeline_result.hybrid_risk_analysis:
        for r in pipeline_result.hybrid_risk_analysis:
            scores[str(r.customer_id)] = float(r.overall_risk_score * 100)
    return scores


@router.get(
    "/rules/suggestions",
    response_model=ApiResponse[List[dict]],
    summary="Get AI-Suggested Rules",
    description="Returns AI-generated rule suggestions based on feature distribution analysis."
)
def get_rule_suggestions(
    pipeline_result: PipelineResult = Depends(get_pipeline_result)
) -> ApiResponse[List[dict]]:
    """Returns AI-suggested rules for human review."""
    try:
        anomaly_scores = _get_anomaly_scores(pipeline_result)
        suggestions = _engine.suggest_rules(
            features_df=pipeline_result.customer_features,
            anomaly_scores=anomaly_scores
        )
        return ApiResponse(data=[s.to_dict() for s in suggestions])
    except Exception as e:
        logger.error(f"Failed to generate rule suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate rule suggestions.")


@router.post(
    "/rules/approve/{rule_name}",
    response_model=ApiResponse[dict],
    summary="Approve a Suggested Rule",
    description="Human analyst approves an AI-suggested rule for deployment."
)
def approve_rule(rule_name: str) -> ApiResponse[dict]:
    """Approve an AI-suggested rule by name."""
    result = _engine.approve_rule(rule_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found in suggestions.")
    return ApiResponse(data=result.to_dict())


@router.post(
    "/rules/reject/{rule_name}",
    response_model=ApiResponse[dict],
    summary="Reject a Suggested Rule",
    description="Human analyst rejects an AI-suggested rule."
)
def reject_rule(rule_name: str) -> ApiResponse[dict]:
    """Reject an AI-suggested rule by name."""
    result = _engine.reject_rule(rule_name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found in suggestions.")
    return ApiResponse(data=result.to_dict())
