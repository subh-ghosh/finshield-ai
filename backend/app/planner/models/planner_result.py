"""Enriched PlannerResult dataclass with full observability metadata."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class PlannerResult:
    """Final investigation result with core output and full observability metadata.

    Attributes:
        customer_id: Investigated customer identifier.
        final_report: Structured investigation report text.
        recommendation: Recommended action (e.g., File SAR, Monitor, Clear).
        confidence: Confidence level string (e.g., HIGH, MEDIUM).
        investigation_complete: Whether investigation reached a definitive conclusion.
        correlation_id: UUID propagated across all API calls for end-to-end tracing.
        tool_calls: Ordered list of tool names invoked during investigation.
        api_calls: Total REST API HTTP calls made.
        reasoning_steps: LLM reasoning summaries per iteration.
        execution_time_ms: End-to-end wall time in milliseconds.
        planner_status: Final planner status (COMPLETED, FAILED, PARTIAL).
        errors: Any non-fatal errors encountered during investigation.
    """
    # Core output
    customer_id: str
    final_report: str
    recommendation: str
    confidence: str
    investigation_complete: bool

    # Traceability
    correlation_id: str

    # Observability
    tool_calls: List[str] = field(default_factory=list)
    api_calls: int = 0
    reasoning_steps: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    planner_status: str = "COMPLETED"
    errors: List[str] = field(default_factory=list)
