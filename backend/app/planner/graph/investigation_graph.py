"""Enterprise LangGraph Investigation Graph assembly with conditional routing."""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.planner.models.planner_state import PlannerState
from app.planner.nodes.planner_node import planner_node
from app.planner.nodes.analysis_node import analysis_node
from app.planner.nodes.reasoning_node import reasoning_node
from app.planner.nodes.decision_node import decision_node, route, ROUTE_ANALYSIS, ROUTE_REPORT
from app.planner.nodes.report_node import report_node


def build_graph(checkpointer=None):
    """Assembles and compiles the Enterprise Investigation StateGraph.

    Graph topology:
        START → planner_node → analysis_node → reasoning_node → decision_node
                                    ↑                                   |
                                    └─── [needs more tools] ────────────┘
                                                                        |
                                                        [sufficient] ↓
                                                           report_node → END

    The checkpointer is injected at compile time so any LangGraph-compatible
    backend (MemorySaver, PostgresSaver, RedisSaver) can be substituted
    without changing graph logic.

    Args:
        checkpointer: Optional LangGraph checkpoint backend. Defaults to MemorySaver.

    Returns:
        Compiled LangGraph CompiledGraph instance.
    """
    builder = StateGraph(PlannerState)

    # Register all nodes
    builder.add_node("planner_node", planner_node)
    builder.add_node("analysis_node", analysis_node)
    builder.add_node("reasoning_node", reasoning_node)
    builder.add_node("decision_node", decision_node)
    builder.add_node("report_node", report_node)

    # Entry edge
    builder.add_edge(START, "planner_node")

    # Linear sequential edges
    builder.add_edge("planner_node", "analysis_node")
    builder.add_edge("analysis_node", "reasoning_node")
    builder.add_edge("reasoning_node", "decision_node")

    # Conditional edge: decision_node routes to analysis_node or report_node
    builder.add_conditional_edges(
        "decision_node",
        route,
        {
            ROUTE_ANALYSIS: "analysis_node",
            ROUTE_REPORT: "report_node",
        }
    )

    builder.add_edge("report_node", END)

    return builder.compile(checkpointer=checkpointer or MemorySaver())


# Module-level compiled graph singleton
investigation_graph = build_graph()
