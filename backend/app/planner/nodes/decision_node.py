"""Decision node: conditional router determining loop or report generation."""

import time
from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.config.config import get_settings
from app.planner.nodes.planner_node import get_llm
from app.planner.prompts.decision_prompt import DECISION_PROMPT_TEMPLATE
from app.planner.registry.tool_registry import TOOL_REGISTRY
from app.planner.prompts.system_prompt import SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Decision routing constants
ROUTE_REPORT = "report_node"
ROUTE_ANALYSIS = "analysis_node"


async def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Determines whether to generate the final report or loop back to analysis.

    Updates state but routing is determined by the graph's conditional edge
    via the route() function below.

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with investigation_complete flag and recommendation.
    """
    settings = get_settings()
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    tool_history = state.get("tool_history", [])
    pending_tools = state.get("pending_tools", [])
    iteration = state.get("iteration_count", 0)
    max_iter = settings.PLANNER_MAX_ITERATIONS
    reasoning_steps = state.get("reasoning_steps", [])
    tool_outputs = state.get("tool_outputs", [])

    logger.info(f"[CID: {cid}] DecisionNode: Iteration {iteration}/{max_iter}, "
                f"tools_called={tool_history}, pending={pending_tools}")
    start = time.perf_counter()

    # Fast path: pending tools still queued → continue analysis
    if pending_tools:
        logger.info(f"[CID: {cid}] DecisionNode: Pending tools remain — routing to analysis_node")
        return {
            "investigation_complete": False,
            "current_status": "NEEDS_MORE_TOOLS",
        }

    # Hard stop: max iterations reached
    if iteration >= max_iter:
        logger.info(f"[CID: {cid}] DecisionNode: Max iterations reached — routing to report_node")
        return {
            "investigation_complete": True,
            "current_status": "MAX_ITERATIONS_REACHED",
        }

    # LLM decision: sufficient evidence or need more?
    available_remaining = [t for t in TOOL_REGISTRY.list_tools() if t not in tool_history]
    evidence_summary = "\n".join(
        [f"- {o.get('tool', '?')}: {str(o.get('output', {}))[:300]}" for o in tool_outputs]
    ) or "No evidence collected yet."

    decision_text = "SUFFICIENT"
    try:
        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=DECISION_PROMPT_TEMPLATE.format(
                customer_id=customer_id,
                tool_history=tool_history,
                iteration=iteration,
                max_iterations=max_iter,
                evidence_summary=evidence_summary,
                reasoning_steps="\n".join(reasoning_steps[-2:]),
                remaining_tools=available_remaining
            ))
        ])
        decision_text = response.content.strip().upper()
    except Exception as e:
        logger.error(f"[CID: {cid}] DecisionNode LLM error: {e} — defaulting to SUFFICIENT")
        decision_text = "SUFFICIENT"

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] DecisionNode: Decision = '{decision_text}' ({elapsed:.2f}ms)")

    if decision_text.startswith("NEEDS_MORE:"):
        next_tool = decision_text.split(":", 1)[1].strip().lower()
        if next_tool in TOOL_REGISTRY.list_tools() and next_tool not in tool_history:
            return {
                "investigation_complete": False,
                "pending_tools": [next_tool],
                "current_status": "NEEDS_MORE_TOOLS",
                "planner_timeline": [{
                    "stage": "decision_node",
                    "decision": "NEEDS_MORE",
                    "next_tool": next_tool,
                    "duration_ms": round(elapsed, 2),
                    "correlation_id": cid
                }]
            }

    # Default: sufficient evidence
    return {
        "investigation_complete": True,
        "current_status": "EVIDENCE_SUFFICIENT",
        "planner_timeline": [{
            "stage": "decision_node",
            "decision": "SUFFICIENT",
            "duration_ms": round(elapsed, 2),
            "correlation_id": cid
        }]
    }


def route(state: Dict[str, Any]) -> str:
    """Conditional edge router for the LangGraph StateGraph.

    Args:
        state: Current PlannerState dict.

    Returns:
        Next node name string.
    """
    if state.get("investigation_complete", False):
        return ROUTE_REPORT
    return ROUTE_ANALYSIS
