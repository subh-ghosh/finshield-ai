"""Reasoning node: LLM reasons over collected tool outputs and produces reasoning steps."""

import json
import time
from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.nodes.planner_node import get_llm
from app.planner.prompts.system_prompt import SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)

_REASONING_PROMPT = """You are an AML evidence analyst reviewing tool outputs from the FinShield backend.

Customer ID: {customer_id}

Latest tool output:
{tool_output}

All tool outputs so far:
{all_outputs}

Instructions:
1. Extract the key risk findings from the tool outputs.
2. Identify triggered rules, anomaly scores, risk levels, and evidence items.
3. Note any gaps in evidence that would require additional tool calls.
4. Never fabricate data — only reference what is present in the tool outputs.

Produce a concise reasoning step (3-5 sentences) summarizing:
- What was found
- What risk indicators are present
- Whether evidence is sufficient for a final recommendation
"""


async def reasoning_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Reasons over the latest tool output using an LLM.

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with new reasoning_step and timeline entry.
    """
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    tool_outputs = state.get("tool_outputs", [])
    iteration = state.get("iteration_count", 0) + 1

    logger.info(f"[CID: {cid}] ReasoningNode: Iteration {iteration} — reasoning over {len(tool_outputs)} tool output(s)")
    start = time.perf_counter()

    latest_output = tool_outputs[-1] if tool_outputs else {}
    all_outputs_text = json.dumps(tool_outputs, indent=2, default=str)
    latest_text = json.dumps(latest_output, indent=2, default=str)

    reasoning_step = ""
    llm = get_llm()

    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=_REASONING_PROMPT.format(
                customer_id=customer_id,
                tool_output=latest_text,
                all_outputs=all_outputs_text
            ))
        ])
        reasoning_step = response.content.strip()
    except Exception as e:
        reasoning_step = f"[Reasoning error at iteration {iteration}: {str(e)}]"
        logger.error(f"[CID: {cid}] ReasoningNode LLM error: {e}")

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] ReasoningNode: Iteration {iteration} complete ({elapsed:.2f}ms)")

    return {
        "reasoning_steps": [reasoning_step],
        "iteration_count": iteration,
        "current_status": "REASONING_COMPLETE",
        "planner_timeline": [{
            "stage": "reasoning_node",
            "iteration": iteration,
            "duration_ms": round(elapsed, 2),
            "correlation_id": cid
        }]
    }
