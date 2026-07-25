"""Enterprise Investigation Planner service — public API with feature flag routing."""

import time
import uuid
from typing import Optional

from app.planner.config.config import get_settings
from app.planner.models.planner_result import PlannerResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def _run_enterprise_planner(
    customer_id: str,
    user_request: str,
    correlation_id: str,
) -> PlannerResult:
    """Executes the enterprise LangGraph investigation planner.

    Args:
        customer_id: Target customer identifier.
        user_request: Natural language investigation request.
        correlation_id: UUID for end-to-end tracing.

    Returns:
        PlannerResult with full investigation output and observability metadata.
    """
    from app.planner.graph.investigation_graph import investigation_graph

    settings = get_settings()
    thread_id = f"{customer_id}-{correlation_id[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "user_request": user_request,
        "customer_id": customer_id,
        "correlation_id": correlation_id,
        "tool_history": [],
        "pending_tools": [],
        "tool_outputs": [],
        "reasoning_steps": [],
        "current_status": "INITIATED",
        "investigation_complete": False,
        "iteration_count": 0,
        "recommendation": "",
        "final_report": "",
        "planner_timeline": [],
        "errors": [],
    }

    start = time.perf_counter()
    logger.info(f"[CID: {correlation_id}] PlannerService: Starting enterprise investigation for '{customer_id}'")

    final_state = {}
    try:
        async for chunk in investigation_graph.astream(initial_state, config):
            final_state.update(list(chunk.values())[-1] if chunk else {})
    except Exception as e:
        logger.error(f"[CID: {correlation_id}] PlannerService: Graph execution error: {e}")
        elapsed = (time.perf_counter() - start) * 1000.0
        return PlannerResult(
            customer_id=customer_id,
            final_report=f"Investigation failed: {str(e)}",
            recommendation="REQUIRES_MANUAL_REVIEW",
            confidence="LOW",
            investigation_complete=False,
            correlation_id=correlation_id,
            tool_calls=final_state.get("tool_history", []),
            api_calls=len(final_state.get("tool_history", [])),
            reasoning_steps=final_state.get("reasoning_steps", []),
            execution_time_ms=round(elapsed, 2),
            planner_status="FAILED",
            errors=[str(e)],
        )

    elapsed = (time.perf_counter() - start) * 1000.0
    tool_calls = final_state.get("tool_history", [])
    logger.info(
        f"[CID: {correlation_id}] PlannerService: Investigation complete for '{customer_id}' "
        f"({elapsed:.2f}ms, {len(tool_calls)} tools called)"
    )

    return PlannerResult(
        customer_id=customer_id,
        final_report=final_state.get("final_report", ""),
        recommendation=final_state.get("recommendation", "REQUIRES_REVIEW"),
        confidence=_extract_confidence(final_state.get("reasoning_steps", [])),
        investigation_complete=final_state.get("investigation_complete", False),
        correlation_id=correlation_id,
        tool_calls=tool_calls,
        api_calls=len(tool_calls),
        reasoning_steps=final_state.get("reasoning_steps", []),
        execution_time_ms=round(elapsed, 2),
        planner_status="COMPLETED" if final_state.get("investigation_complete") else "PARTIAL",
        errors=final_state.get("errors", []),
    )


def _run_legacy_planner(customer_id: str, user_request: str) -> PlannerResult:
    """Delegates to legacy app.agent.graph planner (synchronous, backward-compatible).

    Args:
        customer_id: Target customer identifier.
        user_request: Natural language investigation request.

    Returns:
        PlannerResult with basic output from legacy planner.
    """
    from langchain_core.messages import HumanMessage
    from app.agent.graph import get_agent_executor

    logger.info(f"PlannerService: Using LEGACY planner for '{customer_id}'")
    start = time.perf_counter()

    try:
        graph = get_agent_executor()
        result = graph.invoke(
            {"messages": [HumanMessage(content=user_request)], "customer_id": customer_id},
            config={"configurable": {"thread_id": customer_id}}
        )
        elapsed = (time.perf_counter() - start) * 1000.0
        rec = result.get("final_recommendation", {})
        return PlannerResult(
            customer_id=customer_id,
            final_report=str(result.get("messages", [""])),
            recommendation=rec.get("risk_level", "UNKNOWN") if isinstance(rec, dict) else "UNKNOWN",
            confidence=rec.get("confidence", "N/A") if isinstance(rec, dict) else "N/A",
            investigation_complete=True,
            correlation_id="legacy",
            tool_calls=[],
            api_calls=0,
            reasoning_steps=[],
            execution_time_ms=round(elapsed, 2),
            planner_status="COMPLETED",
            errors=[],
        )
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000.0
        logger.error(f"PlannerService: Legacy planner error: {e}")
        return PlannerResult(
            customer_id=customer_id,
            final_report=f"Legacy planner error: {str(e)}",
            recommendation="REQUIRES_MANUAL_REVIEW",
            confidence="LOW",
            investigation_complete=False,
            correlation_id="legacy",
            execution_time_ms=round(elapsed, 2),
            planner_status="FAILED",
            errors=[str(e)],
        )


def _extract_confidence(reasoning_steps: list) -> str:
    """Infers confidence level from reasoning steps text."""
    if not reasoning_steps:
        return "LOW"
    combined = " ".join(reasoning_steps).upper()
    if "HIGH CONFIDENCE" in combined or "STRONGLY INDICATES" in combined:
        return "HIGH"
    if "MEDIUM" in combined or "SUGGESTS" in combined:
        return "MEDIUM"
    return "MEDIUM"


async def run_investigation(
    customer_id: str,
    user_request: str,
    correlation_id: Optional[str] = None,
) -> PlannerResult:
    """Public entry point for investigation orchestration.

    Routes to enterprise or legacy planner based on PLANNER_USE_ENTERPRISE setting.

    Args:
        customer_id: Target customer identifier.
        user_request: Natural language investigation request.
        correlation_id: Optional UUID for tracing. Auto-generated if not provided.

    Returns:
        PlannerResult with investigation output and observability metadata.
    """
    cid = correlation_id or str(uuid.uuid4())
    settings = get_settings()

    if settings.PLANNER_USE_ENTERPRISE:
        logger.info(f"[CID: {cid}] PlannerService: Routing to ENTERPRISE planner.")
        return await _run_enterprise_planner(customer_id, user_request, cid)
    else:
        logger.info(f"[CID: {cid}] PlannerService: Routing to LEGACY planner.")
        return _run_legacy_planner(customer_id, user_request)
