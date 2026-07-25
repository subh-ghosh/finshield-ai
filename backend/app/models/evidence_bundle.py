"""Evidence bundle containing rule, model, and behavioral evidence collections."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from app.models.evidence_item import EvidenceItem

@dataclass
class EvidenceBundle:
    """Holds structured evidence categories extracted from various stages of evaluation."""
    rule_evidence: List[EvidenceItem] = field(default_factory=list)
    ml_evidence: List[EvidenceItem] = field(default_factory=list)
    behavioral_evidence: List[EvidenceItem] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
