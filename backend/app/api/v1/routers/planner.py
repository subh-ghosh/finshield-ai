"""Enterprise Investigation Planner REST router — POST /api/v1/planner/investigate."""

import uuid
import json
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from app.api.v1.dependencies import get_pipeline_result
from fastapi import Depends
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Investigation Planner"])


class InvestigateRequest(BaseModel):
    """Request model for triggering an AML investigation."""
    customer_id: str = Field(
        default="UNKNOWN",
        description="Target customer identifier. Use 'UNKNOWN' for dataset-level queries.",
        examples=["C_1200", "UNKNOWN"]
    )
    request: str = Field(
        default="Perform a full AML investigation for this customer.",
        description="Natural language investigation request. Can be a dataset-level query."
    )
    use_enterprise: Optional[bool] = Field(
        default=None,
        description="Override PLANNER_USE_ENTERPRISE setting for this request."
    )


class InvestigateResponse(BaseModel):
    """Response model for investigation results."""
    customer_id: str
    user_request: str
    correlation_id: str
    planner_status: str
    investigation_complete: bool
    recommendation: str
    confidence: str
    final_report: str
    tool_calls: List[str]
    api_calls: int
    reasoning_steps: List[str]
    execution_time_ms: float
    errors: List[str]
    # Intent parsing — shows what the agent extracted from the query
    filters_extracted: Optional[Dict[str, Any]] = None
    # V2 multi-agent fields
    planner_timeline: Optional[List[Dict[str, Any]]] = None
    evidence_graph: Optional[Dict[str, Any]] = None


@router.post(
    "/planner/investigate",
    response_model=InvestigateResponse,
    status_code=status.HTTP_200_OK,
    summary="Enterprise AML Investigation",
    description="Runs a deterministic AML investigation for a customer via the REST API."
)
async def investigate(
    body: InvestigateRequest,
    x_correlation_id: Optional[str] = Header(default=None, alias="X-Correlation-ID"),
    pipeline_res = Depends(get_pipeline_result)
) -> InvestigateResponse:
    """Triggers the enterprise investigation planner for a given customer."""
    from app.orchestrator.engine import InvestigationOrchestrator

    cid = x_correlation_id or str(uuid.uuid4())

    logger.info(f"[CID: {cid}] POST /planner/investigate — customer={body.customer_id}")

    # For backward compatibility with ID formats
    customer_id = body.customer_id
    if customer_id.startswith("CUST-"):
        customer_id = customer_id.replace("CUST-", "C_")

    try:
        orchestrator = InvestigationOrchestrator()
        result = await orchestrator.investigate(customer_id=customer_id, pipeline_res=pipeline_res)
    except Exception as e:
        logger.error(f"[CID: {cid}] Investigation endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

    # ── V2: also run the multi-agent LangGraph pipeline to get agent timeline
    #        and structured evidence graph. We run it in a try/except so a
    #        failure here never breaks the existing enterprise response.
    planner_timeline = None
    evidence_graph = None
    filters_extracted = {}
    
    # Defaults fallback to deterministic pipeline
    final_recommendation = result.recommendation
    final_confidence = str(result.confidence)
    final_report = result.executive_summary or "Report generation failed."
    final_reasoning = [f"{evt['action']}: {evt['description']}" for evt in result.timeline]
    
    try:
        from app.agent.graph import get_agent_executor
        from langchain_core.messages import HumanMessage
        agent = get_agent_executor()
        thread_cfg = {"configurable": {"thread_id": f"{customer_id}-{cid}"}}
        # FIX: Pass the actual user request text, not a hardcoded string
        user_request_text = body.request or f"Investigate customer {customer_id}"
        agent_input = {
            "messages": [HumanMessage(content=user_request_text)],
            "customer_id": customer_id,
            "user_request": user_request_text,
        }
        agent_result = await agent.ainvoke(agent_input, config=thread_cfg)
        
        # Extract Timeline
        raw_timeline = agent_result.get("planner_timeline", [])
        planner_timeline = [dict(t) for t in raw_timeline]
        if planner_timeline:
            final_reasoning = [f"{t.get('tool', 'Agent')}: {t.get('result', '')}" for t in planner_timeline]
            
            # Extract filters from the timeline entry (from Supervisor)
            # We don't have filters_extracted explicitly in planner_timeline anymore,
            # but we can grab it from agent_result if it was placed there.
            pass
            
        # Extract Recommendation & Report
        rec = agent_result.get("final_recommendation")
        if rec:
            final_recommendation = rec.get("risk_level", final_recommendation)
            final_confidence = rec.get("confidence", final_confidence)
            
        # The summary message is usually the second to last AI message (before audit)
        messages = agent_result.get("messages", [])
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if "Consensus Reached:" in content:
                final_report = content
                break
                
        # evidence_graph is embedded in the Evidence Aggregator AIMessage
        for msg in reversed(messages):
            content = getattr(msg, "content", "")
            if "Evidence Graph:" in content:
                try:
                    evidence_graph = json.loads(content.split("Evidence Graph: ", 1)[1])
                except Exception:
                    pass
                break
    except Exception as agent_err:
        logger.warning(f"[CID: {cid}] V2 agent pipeline skipped: {agent_err}")

    return InvestigateResponse(
        customer_id=result.customer_id,
        user_request=body.request,
        correlation_id=result.correlation_id,
        planner_status="COMPLETED",
        investigation_complete=True,
        recommendation=final_recommendation,
        confidence=final_confidence,
        final_report=final_report,
        tool_calls=["LoadCustomerStage", "RuleEngineStage", "IsolationForestStage", "HybridRiskStage", "EvidenceAggregationStage"],
        api_calls=1,
        reasoning_steps=final_reasoning,
        execution_time_ms=result.execution_time_ms,
        errors=[],
        filters_extracted=filters_extracted or {},
        planner_timeline=planner_timeline,
        evidence_graph=evidence_graph,
    )


@router.post(
    "/customer/{customer_id}/simulate-counterfactual",
    status_code=status.HTTP_200_OK,
    summary="Counterfactual Risk Simulator",
    description="Simulates parameter shifts and counterfactual decision sensitivity deterministically."
)
async def simulate_counterfactual(
    customer_id: str,
    body: dict,
    pipeline_res = Depends(get_pipeline_result)
):
    from app.models.counterfactual import CounterfactualSimulationRequest
    from app.services.counterfactual_simulator import CounterfactualRiskSimulator
    from app.orchestrator.engine import InvestigationOrchestrator

    clean_id = customer_id.replace("CUST-", "C_")
    
    # Get baseline evaluation
    orchestrator = InvestigationOrchestrator()
    inv_res = await orchestrator.investigate(customer_id=clean_id, pipeline_res=pipeline_res)

    req = CounterfactualSimulationRequest(
        customer_id=clean_id,
        additional_cash_deposits_count=int(body.get("additional_cash_deposits_count", 0)),
        additional_cash_deposit_amount=float(body.get("additional_cash_deposit_amount", 0.0)),
        cross_border_transfer_change_pct=float(body.get("cross_border_transfer_change_pct", 0.0)),
        velocity_multiplier=float(body.get("velocity_multiplier", 1.0))
    )

    simulator = CounterfactualRiskSimulator()
    baseline_score = float(inv_res.risk_score) * 100.0 if inv_res.risk_score <= 1.0 else float(inv_res.risk_score)
    result = simulator.simulate(
        request=req,
        baseline_score_0_100=baseline_score,
        baseline_recommendation=inv_res.recommendation
    )

    return result

