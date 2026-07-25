"""Planner node: parses user intent and seeds the initial tool execution plan."""

import time
from typing import Any, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.config.config import get_settings
from app.planner.registry.tool_registry import TOOL_REGISTRY
from app.planner.prompts.system_prompt import SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IntentPlan(BaseModel):
    """Structured output from the planner LLM for intent and tool selection."""
    intent: str = Field(description="Brief description of the investigation intent.")
    tools_to_call: list[str] = Field(
        description="Ordered list of tool names to call. Must be from available tools only."
    )
    customer_id: str = Field(
        default="UNKNOWN",
        description="Customer ID extracted from user request."
    )


def get_llm():
    """Returns the configured LLM instance."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        settings = get_settings()
        return ChatGoogleGenerativeAI(
            model=settings.PLANNER_LLM_MODEL,
            temperature=settings.PLANNER_LLM_TEMPERATURE
        )
    except Exception as e:
        logger.warning(f"LLM initialization failed: {e}")
        return None


async def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parses user request intent and determines the initial tool execution sequence.

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with correlation_id, pending_tools, and timeline entry.
    """
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    user_request = state.get("user_request", "")

    logger.info(f"[CID: {cid}] PlannerNode: Analyzing intent for customer '{customer_id}'")
    start = time.perf_counter()

    available_tools = TOOL_REGISTRY.list_tools()

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(IntentPlan)
        result = await structured_llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"User Request: {user_request}\n"
                f"Customer ID: {customer_id}\n"
                f"Available tools: {available_tools}\n\n"
                "Select the minimum set of tools needed to investigate this customer. "
                "Always include 'analyze_customer' as the primary tool."
            ))
        ])
        pending = [t for t in result.tools_to_call if t in available_tools]
        if not pending:
            pending = ["analyze_customer"]
        cid_resolved = result.customer_id if result.customer_id != "UNKNOWN" else customer_id

    except Exception as e:
        logger.error(f"[CID: {cid}] PlannerNode LLM error: {e}")
        pending = ["analyze_customer"]
        cid_resolved = customer_id

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] PlannerNode: Plan = {pending} ({elapsed:.2f}ms)")

    return {
        "customer_id": cid_resolved,
        "pending_tools": pending,
        "current_status": "PLANNING_COMPLETE",
        "iteration_count": 0,
        "investigation_complete": False,
        "planner_timeline": [{
            "stage": "planner_node",
            "tools_planned": pending,
            "duration_ms": round(elapsed, 2),
            "correlation_id": cid
        }]
    }
