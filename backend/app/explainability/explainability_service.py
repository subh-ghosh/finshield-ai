"""Explainability service orchestrator executing the end-to-end audit generation pipeline."""

import time
import uuid
from typing import Optional
from app.config import service_metadata
from app.config import PIPELINE_VERSION
from app.explainability.interfaces.i_explainability_service import IExplainabilityService
from app.explainability.interfaces.i_evidence_extractor import IEvidenceExtractor
from app.explainability.interfaces.i_evidence_ranker import IEvidenceRanker
from app.explainability.interfaces.i_timeline_builder import ITimelineBuilder
from app.explainability.interfaces.i_summary_generator import ISummaryGenerator
from app.explainability.interfaces.i_explanation_builder import IExplanationBuilder
from app.explainability.evidence_extractor import EvidenceExtractor
from app.explainability.evidence_ranker import EvidenceRanker
from app.explainability.timeline_builder import TimelineBuilder
from app.explainability.summary_generator import SummaryGenerator
from app.explainability.explanation_builder import ExplanationBuilder
from app.models.explainability_context import ExplainabilityContext
from app.models.explanation_response import ExplanationResponseV1
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ExplainabilityService(IExplainabilityService):
    """Orchestrates evidence extraction, ranking, summary generation, and timeline compilation into ExplanationResponses."""

    def __init__(
        self,
        extractor: Optional[IEvidenceExtractor] = None,
        ranker: Optional[IEvidenceRanker] = None,
        timeline_builder: Optional[ITimelineBuilder] = None,
        summary_generator: Optional[ISummaryGenerator] = None,
        builder: Optional[IExplanationBuilder] = None
    ):
        """Initializes ExplainabilityService with its sub-services.

        Args:
            extractor: Component compiling evidence items.
            ranker: Component ordering evidence items.
            timeline_builder: Component generating chronology events.
            summary_generator: Component formatting text narratives.
            builder: Component mapping structural details.
        """
        self.extractor = extractor or EvidenceExtractor()
        self.ranker = ranker or EvidenceRanker()
        self.timeline_builder = timeline_builder or TimelineBuilder()
        self.summary_generator = summary_generator or SummaryGenerator()
        self.builder = builder or ExplanationBuilder()

    def explain(self, context: ExplainabilityContext) -> ExplanationResponseV1:
        """Runs explainability steps and returns the ExplanationResponseV1 contract.

        Args:
            context: Execution context containing features, results, and config options.

        Returns:
            ExplanationResponseV1: Consolidated case explanation response.
        """
        logger.info("Explainability Service evaluation started...")
        start_total = time.perf_counter()

        res = context.hybrid_result

        # 1. Extractor Evidence
        extract_start = time.perf_counter()
        raw_bundle = context.evidence_bundle
        # Re-extract only if bundle is empty
        if not raw_bundle.rule_evidence and not raw_bundle.ml_evidence and not raw_bundle.behavioral_evidence:
            raw_features = context.pipeline_metadata.get("raw_features", {})
            raw_bundle = self.extractor.extract(res, raw_features)
        extract_time = (time.perf_counter() - extract_start) * 1000.0

        # Calculate counts
        raw_evidence_list = raw_bundle.rule_evidence + raw_bundle.ml_evidence + raw_bundle.behavioral_evidence
        evidence_count = len(raw_evidence_list)

        # 2. Rank Evidence
        rank_start = time.perf_counter()
        ranked_bundle = self.ranker.rank(raw_bundle)
        rank_time = (time.perf_counter() - rank_start) * 1000.0

        ranked_evidence_list = ranked_bundle.rule_evidence + ranked_bundle.ml_evidence + ranked_bundle.behavioral_evidence
        ranked_evidence_count = len(ranked_evidence_list)

        # Update context bundle with ranked copy
        context.evidence_bundle = ranked_bundle

        # 3. Generate Summary Narrative
        summary_start = time.perf_counter()
        summary_report = self.summary_generator.generate_summary(context)
        summary_time = (time.perf_counter() - summary_start) * 1000.0

        # 4. Compile Timeline Events
        timeline_start = time.perf_counter()
        timeline_list = self.timeline_builder.build_timeline(res, context.pipeline_metadata)
        timeline_time = (time.perf_counter() - timeline_start) * 1000.0

        # 5. Build Explanation JSON structure
        build_start = time.perf_counter()
        explanation_map = self.builder.build(context)
        build_time = (time.perf_counter() - build_start) * 1000.0

        total_time = (time.perf_counter() - start_total) * 1000.0

        # Build Versioned metadata section
        metadata_dict = {
            "api_version": service_metadata.API_VERSION,
            "schema_version": service_metadata.SCHEMA_VERSION,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "generator": {
                "service_name": service_metadata.SERVICE_NAME,
                "service_version": service_metadata.SERVICE_VERSION,
                "environment": getattr(service_metadata, "DEFAULT_ENVIRONMENT", "development")
            },
            "request_id": context.pipeline_metadata.get("request_id", str(uuid.uuid4())),
            "pipeline_version": PIPELINE_VERSION,
            "engine_version": res.engine_version
        }

        # Build metrics section
        metrics_dict = {
            "evidence_count": evidence_count,
            "ranked_evidence_count": ranked_evidence_count,
            "timeline_event_count": len(timeline_list),
            "evidence_extraction_time_ms": extract_time,
            "evidence_ranking_time_ms": rank_time,
            "summary_generation_time_ms": summary_time,
            "timeline_compilation_time_ms": timeline_time,
            "explanation_building_time_ms": build_time,
            "explanation_generation_time_ms": total_time,
            "serialization_time_ms": 0.0,  # Populated later during serialization if active
            "output_format": "raw",
            "warnings": []
        }

        response = ExplanationResponseV1(
            response_id=f"RES-{uuid.uuid4().hex[:12].upper()}",
            customer_id=res.customer_id,
            overall_risk_score=res.overall_risk_score,
            severity=res.severity,
            confidence=res.confidence,
            summary=summary_report.narrative,
            recommendation=res.recommendation,
            risk_breakdown={
                "rule_score": res.score_breakdown.rule_score,
                "ml_score": res.score_breakdown.ml_score,
                "behavioral_score": res.score_breakdown.behavioral_score,
                "overall_score": res.score_breakdown.overall_score
            },
            evidence=ranked_evidence_list,
            explanation=explanation_map,
            timeline=timeline_list,
            metadata=metadata_dict,
            metrics=metrics_dict
        )

        logger.info(f"Explainability Response compiled successfully in {total_time:.2f}ms.")
        return response

    def explain_from_agent_graph(self, evidence_graph: dict) -> str:
        """V2 entry point: generates a natural-language explanation from the
        structured evidence graph produced by the multi-agent LangGraph pipeline.

        This is additive — it does NOT replace the existing ``explain()`` method
        used by the classic enterprise pipeline.

        Args:
            evidence_graph: Dict with ``layers`` and ``attribution`` keys.

        Returns:
            str: Human-readable attribution explanation.
        """
        return self.extractor.explain_evidence_graph(evidence_graph)
