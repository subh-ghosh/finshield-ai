"""Explainability services and reports generation subpackage."""

# Interfaces
from app.explainability.interfaces.i_explainability_service import IExplainabilityService
from app.explainability.interfaces.i_evidence_extractor import IEvidenceExtractor
from app.explainability.interfaces.i_evidence_ranker import IEvidenceRanker
from app.explainability.interfaces.i_timeline_builder import ITimelineBuilder
from app.explainability.interfaces.i_summary_generator import ISummaryGenerator
from app.explainability.interfaces.i_explanation_builder import IExplanationBuilder
from app.explainability.interfaces.i_explanation_policy import IExplanationPolicy
from app.explainability.interfaces.i_output_serializer import IOutputSerializer

# Core implementations
from app.explainability.evidence_extractor import EvidenceExtractor
from app.explainability.evidence_ranker import EvidenceRanker
from app.explainability.timeline_builder import TimelineBuilder
from app.explainability.summary_generator import SummaryGenerator
from app.explainability.explanation_builder import ExplanationBuilder
from app.explainability.explainability_service import ExplainabilityService

# Policies
from app.explainability.policies.deterministic_explanation_policy import DeterministicExplanationPolicy

# Serializers
from app.explainability.serializers.json_serializer import JSONSerializer
from app.explainability.serializers.markdown_serializer import MarkdownSerializer
from app.explainability.serializers.plain_text_serializer import PlainTextSerializer
from app.explainability.serializers.planner_context_serializer import PlannerContextSerializer

__all__ = [
    # Interfaces
    "IExplainabilityService",
    "IEvidenceExtractor",
    "IEvidenceRanker",
    "ITimelineBuilder",
    "ISummaryGenerator",
    "IExplanationBuilder",
    "IExplanationPolicy",
    "IOutputSerializer",
    
    # Core implementations
    "EvidenceExtractor",
    "EvidenceRanker",
    "TimelineBuilder",
    "SummaryGenerator",
    "ExplanationBuilder",
    "ExplainabilityService",
    
    # Policies
    "DeterministicExplanationPolicy",
    
    # Serializers
    "JSONSerializer",
    "MarkdownSerializer",
    "PlainTextSerializer",
    "PlannerContextSerializer"
]
