"""Report node: generates the final structured investigation report using LLM."""

import json
import time
from typing import Any, Dict
from langchain_core.messages import HumanMessage, SystemMessage
from app.planner.nodes.planner_node import get_llm
from app.planner.prompts.system_prompt import SYSTEM_PROMPT
from app.planner.prompts.report_prompt import REPORT_PROMPT_TEMPLATE
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _extract_field(tool_outputs: list, field: str, default: str = "UNKNOWN") -> str:
    """Safely extracts a named field from the first tool output containing it."""
    for entry in tool_outputs:
        output = entry.get("output", {})
        if isinstance(output, dict) and field in output:
            return str(output[field])
    return default


def _format_evidence(tool_outputs: list) -> str:
    """Formats evidence items from tool outputs for the report prompt."""
    for entry in tool_outputs:
        output = entry.get("output", {})
        if isinstance(output, dict) and "evidence" in output:
            evidence = output["evidence"]
            if isinstance(evidence, list):
                lines = []
                for i, item in enumerate(evidence, 1):
                    if isinstance(item, dict):
                        lines.append(
                            f"{i}. [{item.get('source', '?')}] {item.get('description', item.get('text', ''))}"
                        )
                    else:
                        lines.append(f"{i}. {item}")
                return "\n".join(lines) or "No evidence items available."
    return "No evidence items available."


def _format_timeline(tool_outputs: list) -> str:
    """Formats timeline events from tool outputs for the report prompt."""
    for entry in tool_outputs:
        output = entry.get("output", {})
        if isinstance(output, dict) and "timeline" in output:
            timeline = output["timeline"]
            if isinstance(timeline, list):
                lines = [
                    f"- [{e.get('timestamp', '?')}] {e.get('event', e.get('description', str(e)))}"
                    for e in timeline
                    if isinstance(e, dict)
                ]
                return "\n".join(lines) or "No timeline events available."
    return "No timeline events available."


async def report_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Generates the final structured investigation report.

    Args:
        state: Current PlannerState dict.

    Returns:
        State updates with final_report, recommendation, and timeline entry.
    """
    cid = state.get("correlation_id", "")
    customer_id = state.get("customer_id", "UNKNOWN")
    tool_outputs = state.get("tool_outputs", [])
    reasoning_steps = state.get("reasoning_steps", [])

    logger.info(f"[CID: {cid}] ReportNode: Generating final report for '{customer_id}'")
    start = time.perf_counter()

    risk_score = _extract_field(tool_outputs, "overall_risk_score", "N/A")
    severity = _extract_field(tool_outputs, "severity", "UNKNOWN")
    recommendation = _extract_field(tool_outputs, "recommendation", "REQUIRES_REVIEW")
    confidence = _extract_field(tool_outputs, "confidence", "MEDIUM")
    evidence_text = _format_evidence(tool_outputs)
    timeline_text = _format_timeline(tool_outputs)

    risk_summary = (
        f"Risk Score: {risk_score}\n"
        f"Severity: {severity}\n"
        f"Recommendation: {recommendation}\n"
        f"Confidence: {confidence}"
    )

    final_report = ""

    try:
        llm = get_llm()
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=REPORT_PROMPT_TEMPLATE.format(
                customer_id=customer_id,
                correlation_id=cid,
                risk_summary=risk_summary,
                evidence_items=evidence_text,
                timeline_events=timeline_text,
                reasoning_steps="\n".join(reasoning_steps)
            ))
        ])
        final_report = response.content.strip()
    except Exception as e:
        logger.error(f"[CID: {cid}] ReportNode LLM error: {e}")
        final_report = (
            f"## Investigation Report — {customer_id}\n\n"
            f"{risk_summary}\n\n"
            f"**Evidence:**\n{evidence_text}\n\n"
            f"**Timeline:**\n{timeline_text}\n\n"
            f"*[Report generation encountered an error: {e}]*"
        )

    elapsed = (time.perf_counter() - start) * 1000.0
    logger.info(f"[CID: {cid}] ReportNode: Report generated ({elapsed:.2f}ms)")

    return {
        "final_report": final_report,
        "recommendation": recommendation,
        "current_status": "REPORT_COMPLETE",
        "investigation_complete": True,
        "planner_timeline": [{
            "stage": "report_node",
            "severity": severity,
            "recommendation": recommendation,
            "duration_ms": round(elapsed, 2),
            "correlation_id": cid
        }]
    }
