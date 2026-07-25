from typing import TypedDict, Annotated, Sequence, Any, List, Dict
from langchain_core.messages import BaseMessage
import operator


class EvidenceItem(TypedDict):
    source: str
    description: str


class Recommendation(TypedDict):
    risk_level: str
    confidence: str
    evidence_count: int
    recommended_actions: List[str]


class ActionLog(TypedDict):
    timestamp: str
    tool: str
    duration: float
    result: str
    status: str


def merge_list(a: List[Any], b: List[Any]) -> List[Any]:
    if not a:
        a = []
    if not b:
        b = []
    return a + b


def merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    if not a:
        a = {}
    if not b:
        b = {}
    a.update(b)
    return a


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    customer_id: str

    # Dynamic Planning
    current_intent: str
    execution_plan: List[str]  # List of tool names to execute

    # Execution Monitor
    execution_monitor: Annotated[
        Dict[str, str], merge_dict
    ]  # tool_name -> status (WAITING, RUNNING, COMPLETED, FAILED)

    # Evidence & Recommendation
    evidence_bundle: Annotated[List[EvidenceItem], merge_list]
    final_recommendation: Recommendation

    # Tracing
    planner_timeline: Annotated[List[ActionLog], merge_list]
