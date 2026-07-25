"""Analysis node: dispatches the next pending tool via the tool registry and async API client."""

import time
from typing import Any, Dict
from app.planner.client.api_client import FinShieldAPIClient
from app.planner.client.exceptions import PlannerAPIError
from app.planner.registry.tool_registry import TOOL_REGISTRY
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def analysis_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches the next tool in pending_tools via the shared async API client.

    Sequentially executes tools one per iteration. Updates tool_outputs and tool_history.

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with tool output, updated history, and timeline entry.
    """
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    pending = list(state.get("pending_tools", []))

    if not pending:
        logger.warning(f"[CID: {cid}] AnalysisNode: No pending tools to execute.")
        return {"current_status": "NO_TOOLS", "pending_tools": []}

    # Pop the next tool to execute
    tool_name = pending.pop(0)
    logger.info(f"[CID: {cid}] AnalysisNode: Executing tool '{tool_name}' for customer '{customer_id}'")

    tool = TOOL_REGISTRY.get_tool(tool_name)
    start = time.perf_counter()
    tool_output: Dict[str, Any] = {}
    error_msg: str = ""

    if tool is None:
        error_msg = f"Tool '{tool_name}' not found in registry."
        logger.error(f"[CID: {cid}] AnalysisNode: {error_msg}")
    else:
        try:
            async with FinShieldAPIClient(correlation_id=cid) as client:
                # Pass customer_id for all customer-scoped tools
                tool_output = await tool.execute(client, customer_id=customer_id)
        except PlannerAPIError as e:
            error_msg = f"Tool '{tool_name}' API error: {str(e)}"
            logger.error(f"[CID: {cid}] AnalysisNode: {error_msg}")
            tool_output = {"error": error_msg, "tool": tool_name}
        except Exception as e:
            error_msg = f"Tool '{tool_name}' unexpected error: {str(e)}"
            logger.error(f"[CID: {cid}] AnalysisNode: {error_msg}")
            tool_output = {"error": error_msg, "tool": tool_name}

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] AnalysisNode: Tool '{tool_name}' completed ({elapsed:.2f}ms)")

    updates: Dict[str, Any] = {
        "pending_tools": pending,
        "tool_history": [tool_name],
        "tool_outputs": [{"tool": tool_name, "output": tool_output}],
        "current_status": "ANALYSIS_COMPLETE",
        "planner_timeline": [{
            "stage": "analysis_node",
            "tool": tool_name,
            "duration_ms": round(elapsed, 2),
            "success": not bool(error_msg),
            "correlation_id": cid
        }]
    }
    if error_msg:
        updates["errors"] = [error_msg]

    return updates
