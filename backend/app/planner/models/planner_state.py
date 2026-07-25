"""LangGraph TypedDict state for the Enterprise Investigation Planner."""

import operator
from typing import Annotated, Any, Dict, List, TypedDict


def _merge_list(a: List[Any], b: List[Any]) -> List[Any]:
    return (a or []) + (b or [])


def _merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(a or {})
    merged.update(b or {})
    return merged


class PlannerState(TypedDict):
    """Full LangGraph state tracking investigation lifecycle."""

    # Identity
    user_request: str
    customer_id: str
    correlation_id: str          # UUID propagated across all API calls

    # Tool Orchestration
    tool_history: Annotated[List[str], _merge_list]          # Tools invoked so far
    pending_tools: List[str]                                  # Tools yet to be invoked
    tool_outputs: Annotated[List[Dict[str, Any]], _merge_list]  # Raw API responses

    # LLM Reasoning
    reasoning_steps: Annotated[List[str], _merge_list]       # Reasoning summaries per iteration

    # Decision & Report
    current_status: str
    investigation_complete: bool
    iteration_count: int
    recommendation: str
    final_report: str

    # Audit Trail
    planner_timeline: Annotated[List[Dict[str, Any]], _merge_list]
    errors: Annotated[List[str], _merge_list]
