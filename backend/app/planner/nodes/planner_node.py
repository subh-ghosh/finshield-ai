"""Planner node: parses user intent and seeds the initial tool execution plan."""

import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.config.config import get_settings
from app.planner.registry.tool_registry import TOOL_REGISTRY
from app.planner.prompts.system_prompt import SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IntentPlan(BaseModel):
    """Structured output from the planner LLM for intent and tool selection."""

    intent: str = Field(
        description="Brief description of the investigation intent."
    )
    tools_to_call: List[str] = Field(
        description=(
            "Ordered list of tool names to call. Must be from available tools only. "
            "Use 'eda_analysis' for broad dataset-level queries. "
            "Use 'analyze_customer' for single customer investigations."
        )
    )
    customer_id: str = Field(
        default="UNKNOWN",
        description="Customer ID extracted from the request. 'UNKNOWN' if not specified."
    )
    aml_pattern: Optional[str] = Field(
        default=None,
        description=(
            "AML pattern to focus on, if explicitly mentioned. "
            "One of: STRUCTURING, SMURFING, LAYERING, SHELL, FAN_IN, FAN_OUT, CYCLE. Null if not mentioned."
        )
    )
    date_from: Optional[str] = Field(
        default=None,
        description="Start date filter from query (ISO-8601, e.g. '2024-01-01'). Null if not specified."
    )
    date_to: Optional[str] = Field(
        default=None,
        description="End date filter from query (ISO-8601, e.g. '2024-01-31'). Null if not specified."
    )
    country_filter: Optional[str] = Field(
        default=None,
        description="Country/jurisdiction filter (ISO-3166 code, e.g. 'SG'). Null if not specified."
    )
    transaction_type_filter: Optional[str] = Field(
        default=None,
        description="Transaction type filter. One of: WIRE, CASH, ACH, CRYPTO, SWIFT, TRANSFER. Null if not specified."
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


def _is_dataset_level_query(user_request: str, customer_id: str) -> bool:
    """Returns True if query is broad/dataset-level rather than single-customer."""
    broad_keywords = [
        "dataset", "analyse this", "analyze this", "overview", "summary",
        "all customers", "suspicious activity", "flag high-risk", "how many",
        "what does the data", "distribution", "pattern across", "find all",
        "structuring patterns", "high risk customers", "flag customers",
        "which customers", "across all", "entire dataset",
    ]
    req_lower = user_request.lower()
    is_broad = any(kw in req_lower for kw in broad_keywords)
    no_customer = customer_id in ("UNKNOWN", "", None)
    return is_broad and no_customer


async def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Parses user request intent and determines the initial tool execution sequence.

    Extracts:
    - tools_to_call: ordered list of tools to invoke
    - customer_id: specific customer if targeted
    - aml_pattern: AML typology focus (structuring, smurfing, etc.)
    - date_from / date_to: time window filters
    - country_filter: jurisdiction filter
    - transaction_type_filter: tx type filter

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with pending_tools, filters, and timeline entry.
    """
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    user_request = state.get("user_request", "")

    logger.info(f"[CID: {cid}] PlannerNode: Analyzing intent for customer '{customer_id}'")
    start = time.perf_counter()

    available_tools = TOOL_REGISTRY.list_tools()
    tool_descriptions = {
        name: TOOL_REGISTRY.get_metadata(name).description
        for name in available_tools
        if TOOL_REGISTRY.get_metadata(name)
    }

    # Smart default if LLM fails
    if _is_dataset_level_query(user_request, customer_id):
        default_tools = ["eda_analysis"]
    elif customer_id not in ("UNKNOWN", "", None):
        # For targeted single-customer: feature -> anomaly -> risk_classify -> explain
        default_tools = ["feature_engineering", "anomaly_detection", "risk_classification", "get_explanation"]
    else:
        default_tools = ["analyze_customer"]

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(IntentPlan)
        result = await structured_llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=(
                f"User Request: {user_request}\n"
                f"Customer ID context: {customer_id}\n\n"
                "Available tools:\n"
                + "\n".join(f"  - {name}: {desc}" for name, desc in tool_descriptions.items())
                + "\n\nInstructions:\n"
                "1. Select the MINIMUM set of tools needed for this query.\n"
                "2. For broad dataset queries (no customer specified), use 'eda_analysis'.\n"
                "3. For single customer investigation, use 'analyze_customer' and optionally 'get_explanation'.\n"
                "4. Extract any date filters, country filters, AML pattern, or transaction type from the query.\n"
                "5. If no customer ID is in the query, set customer_id to 'UNKNOWN'.\n"
            ))
        ])
        pending = [t for t in result.tools_to_call if t in available_tools]
        if not pending:
            pending = default_tools
        cid_resolved = (
            result.customer_id
            if result.customer_id not in ("UNKNOWN", "")
            else customer_id
        )

        # Collect extracted filters
        extra_state: Dict[str, Any] = {}
        if result.aml_pattern:
            extra_state["aml_pattern"] = result.aml_pattern
        if result.date_from:
            extra_state["date_from"] = result.date_from
        if result.date_to:
            extra_state["date_to"] = result.date_to
        if result.country_filter:
            extra_state["country_filter"] = result.country_filter
        if result.transaction_type_filter:
            extra_state["transaction_type_filter"] = result.transaction_type_filter

    except Exception as e:
        logger.error(f"[CID: {cid}] PlannerNode LLM error: {e}")
        pending = default_tools
        cid_resolved = customer_id
        extra_state = {}

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] PlannerNode: Plan={pending} filters={extra_state} ({elapsed:.2f}ms)")

    return {
        "customer_id": cid_resolved,
        "pending_tools": pending,
        "current_status": "PLANNING_COMPLETE",
        "iteration_count": 0,
        "investigation_complete": False,
        "planner_timeline": [{
            "stage": "planner_node",
            "tools_planned": pending,
            "filters_extracted": extra_state,
            "duration_ms": round(elapsed, 2),
            "correlation_id": cid,
        }],
        **extra_state,
    }
