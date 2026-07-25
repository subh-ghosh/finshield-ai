"""Audit log timeline event mapping pipeline operations to sequence blocks."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class TimelineEvent:
    """Represents a discrete chronological event recorded during case evaluation."""
    event_name: str
    timestamp: float
    severity: str
    description: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
