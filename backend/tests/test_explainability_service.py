"""Unit and integration test suite for the Enterprise Explainability Service."""

import time
import pytest
from app.config import service_metadata
from app.explainability.interfaces.i_explainability_service import IExplainabilityService
from app.explainability.interfaces.i_output_serializer import IOutputSerializer
from app.explainability.explainability_service import ExplainabilityService
from app.explainability.evidence_extractor import EvidenceExtractor
from app.explainability.evidence_ranker import EvidenceRanker
from app.explainability.timeline_builder import TimelineBuilder
from app.explainability.summary_generator import SummaryGenerator
from app.explainability.explanation_builder import ExplanationBuilder
from app.explainability.policies.deterministic_explanation_policy import DeterministicExplanationPolicy
from app.explainability.serializers.json_serializer import JSONSerializer
from app.explainability.serializers.markdown_serializer import MarkdownSerializer
from app.explainability.serializers.plain_text_serializer import PlainTextSerializer
from app.explainability.serializers.planner_context_serializer import PlannerContextSerializer
from app.models.hybrid_risk_result import HybridRiskResult
from app.models.score_breakdown import ScoreBreakdown
from app.models.explanation import Explanation
from app.models.risk_factor import RiskFactor
from app.models.explainability_context import ExplainabilityContext
from app.models.evidence_bundle import EvidenceBundle
from app.models.evidence_item import EvidenceItem
from app.models.timeline_event import TimelineEvent
from app.models.explanation_response import ExplanationResponseV1

@pytest.fixture
def mock_hybrid_result():
    """Generates a dummy mock of HybridRiskResult for explainability testing."""
    breakdown = ScoreBreakdown(
        rule_score=0.4,
        ml_score=0.25,
        behavioral_score=0.3,
        overall_score=0.345,
        weights_used={"rule_engine": 0.6, "isolation_forest": 0.3, "behavioural": 0.1}
    )
    
    factors = [
        RiskFactor(
            name="RULE_LARGE_TRANSACTION",
            score=15.0,
            severity="LOW",
            description="Large transfer detected",
            source="RULE_ENGINE"
        ),
        RiskFactor(
            name="BEHAVIORAL_VELOCITY_SCORE",
            score=0.8,
            severity="HIGH",
            description="Unusual velocity computed",
            source="BEHAVIORAL"
        )
    ]
    
    return HybridRiskResult(
        customer_id="C_TEST",
        overall_risk_score=0.345,
        severity="MEDIUM",
        confidence=0.85,
        score_breakdown=breakdown,
        triggered_rules=["RULE_LARGE_TRANSACTION"],
        anomaly_score=0.25,
        risk_factors=factors,
        recommendation="Manual Review",
        explanation=Explanation(
            summary="Standard medium risk summary",
            rule_evidence="Rule alerts present",
            ml_evidence="ML score within normal bounds",
            behavioral_evidence="Velocity high"
        ),
        timestamp=time.time()
    )

# ====================================================
# CONTRACT AND METADATA TESTS
# ====================================================

def test_explainability_interfaces():
    """Verifies that explainability modules adhere to contract design interfaces."""
    assert issubclass(ExplainabilityService, IExplainabilityService)
    assert issubclass(JSONSerializer, IOutputSerializer)
    assert issubclass(MarkdownSerializer, IOutputSerializer)
    assert issubclass(PlainTextSerializer, IOutputSerializer)
    assert issubclass(PlannerContextSerializer, IOutputSerializer)

def test_explanation_response_v1_validation():
    """Asserts that ExplanationResponseV1 validates mandatory schema fields upon construction."""
    metadata_ok = {"api_version": "v1", "schema_version": "1.0", "generated_at": "2026-07-25", "generator": "Test"}
    
    # Missing response_id
    with pytest.raises(ValueError, match="response_id is missing"):
        ExplanationResponseV1(
            response_id="", customer_id="C1", overall_risk_score=0.5, severity="LOW", confidence=0.9,
            summary="Ok", recommendation="None", risk_breakdown={}, evidence=[], explanation={}, timeline=[], metadata=metadata_ok
        )
        
    # Missing summary
    with pytest.raises(ValueError, match="summary is missing"):
        ExplanationResponseV1(
            response_id="R1", customer_id="C1", overall_risk_score=0.5, severity="LOW", confidence=0.9,
            summary="", recommendation="None", risk_breakdown={}, evidence=[], explanation={}, timeline=[], metadata=metadata_ok
        )

    # Missing metadata key
    with pytest.raises(ValueError, match="metadata key 'schema_version' is missing"):
        ExplanationResponseV1(
            response_id="R1", customer_id="C1", overall_risk_score=0.5, severity="LOW", confidence=0.9,
            summary="Ok", recommendation="None", risk_breakdown={}, evidence=[], explanation={}, timeline=[],
            metadata={"api_version": "v1", "generated_at": "2026", "generator": "Test"}
        )

def test_service_metadata_configuration():
    """Checks that service metadata loading is correct and not duplicated."""
    assert service_metadata.SERVICE_NAME == "ExplainabilityService"
    assert service_metadata.API_VERSION == "v1"
    assert service_metadata.SERVICE_VERSION == "1.0.0"

# ====================================================
# COMPONENT LEVEL TESTS
# ====================================================

def test_evidence_extractor(mock_hybrid_result):
    """Checks that EvidenceExtractor extracts risk factors and sets correct traceability fields."""
    extractor = EvidenceExtractor()
    bundle = extractor.extract(mock_hybrid_result, {"velocity_score": 8.0})
    
    assert len(bundle.rule_evidence) == 1
    assert len(bundle.behavioral_evidence) == 1
    assert len(bundle.ml_evidence) == 1  # Baseline fallback ML item added
    
    # Check trace mapping
    rule_item = bundle.rule_evidence[0]
    assert rule_item.rule_id == "LARGE_TRANSACTION"
    assert rule_item.pipeline_stage == "RULE_ENGINE"
    
    beh_item = bundle.behavioral_evidence[0]
    assert beh_item.feature_name == "velocity_score"
    assert beh_item.metadata["raw_value"] == 8.0

def test_evidence_ranker_deduplication():
    """Asserts that EvidenceRanker removes exact duplicates and sorts by severity ranks."""
    ranker = EvidenceRanker()
    
    item1 = EvidenceItem("RULE_ENGINE", "DUPE_RULE", "Desc1", "MEDIUM", 0.4, 0.9)
    item2 = EvidenceItem("RULE_ENGINE", "DUPE_RULE", "Desc2", "HIGH", 0.7, 0.9) # Higher score/severity duplicate
    item3 = EvidenceItem("RULE_ENGINE", "CRITICAL_RULE", "Desc3", "CRITICAL", 0.9, 0.9)
    
    bundle = EvidenceBundle(rule_evidence=[item1, item2, item3])
    ranked = ranker.rank(bundle)
    
    # Check deduplication: only 2 unique items remaining
    assert len(ranked.rule_evidence) == 2
    
    # Check sorting: CRITICAL rule first, then HIGH rule
    assert ranked.rule_evidence[0].title == "CRITICAL_RULE"
    assert ranked.rule_evidence[1].title == "DUPE_RULE"
    assert ranked.rule_evidence[1].score == 0.7  # Highest duplicate retained

def test_timeline_builder_ordering(mock_hybrid_result):
    """Verifies that TimelineBuilder places audit events in ascending chronological order."""
    builder = TimelineBuilder()
    timeline = builder.build_timeline(mock_hybrid_result, {})
    
    assert len(timeline) == 5
    # Verify timestamp ordering (ascending)
    for i in range(len(timeline) - 1):
        assert timeline[i].timestamp < timeline[i+1].timestamp

def test_summary_generator_interpolations(mock_hybrid_result):
    """Verifies SummaryGenerator produces deterministic summaries for each severity."""
    # Test Medium Summary
    context = ExplainabilityContext(
        hybrid_result=mock_hybrid_result,
        evidence_bundle=EvidenceBundle(
            behavioral_evidence=[EvidenceItem("BEHAVIORAL", "BEHAVIORAL_VELOCITY_SCORE", "d", "LOW", 0.1, 0.9)]
        )
    )
    generator = SummaryGenerator()
    summary = generator.generate_summary(context)
    
    assert "medium threat signature" in summary.narrative
    assert "velocity_score" in summary.narrative
    
    # Test Critical Summary
    mock_hybrid_result.severity = "CRITICAL"
    summary_crit = generator.generate_summary(context)
    assert "critical threat signature" in summary_crit.narrative

def test_explanation_builder_depth_policies(mock_hybrid_result):
    """Verifies ExplanationBuilder structures output JSON based on policy switching."""
    bundle = EvidenceBundle(
        rule_evidence=[EvidenceItem("RULE_ENGINE", "RULE_R1", "desc", "LOW", 0.2, 0.9)]
    )
    context = ExplainabilityContext(hybrid_result=mock_hybrid_result, evidence_bundle=bundle)
    
    # Default Policy
    builder = ExplanationBuilder()
    explanation_map = builder.build(context)
    assert explanation_map["Overall Risk"] == "MEDIUM"
    assert explanation_map["policy_depth"] == "detailed"

def test_explainability_service_orchestration(mock_hybrid_result):
    """Verifies ExplainabilityService runs end-to-end and returns validated ExplanationResponseV1 packages."""
    service = ExplainabilityService()
    context = ExplainabilityContext(
        hybrid_result=mock_hybrid_result,
        evidence_bundle=EvidenceBundle(),
        pipeline_metadata={"raw_features": {"velocity_score": 8.0}}
    )
    
    response = service.explain(context)
    assert isinstance(response, ExplanationResponseV1)
    assert response.customer_id == "C_TEST"
    assert "evidence_extraction_time_ms" in response.metrics
    assert response.metadata["api_version"] == "v1"

# ====================================================
# SERIALIZERS VERIFICATION
# ====================================================

def test_serializers_outputs(mock_hybrid_result):
    """Tests JSON, Markdown, PlainText, and Planner context serialization output types."""
    service = ExplainabilityService()
    context = ExplainabilityContext(hybrid_result=mock_hybrid_result, evidence_bundle=EvidenceBundle())
    response = service.explain(context)
    
    # JSON
    js = JSONSerializer()
    assert js.get_format_name() == "json"
    js_out = js.serialize(response)
    assert isinstance(js_out, dict)
    assert js_out["customer_id"] == "C_TEST"
    
    # Markdown
    ms = MarkdownSerializer()
    assert ms.get_format_name() == "markdown"
    ms_out = ms.serialize(response)
    assert isinstance(ms_out, str)
    assert "# Investigator Risk Explanation Report" in ms_out
    
    # Plain Text
    pts = PlainTextSerializer()
    assert pts.get_format_name() == "text"
    pts_out = pts.serialize(response)
    assert isinstance(pts_out, str)
    assert "INVESTIGATOR RISK EXPLANATION REPORT" in pts_out
    
    # Planner Context
    ps = PlannerContextSerializer()
    assert ps.get_format_name() == "planner"
    ps_out = ps.serialize(response)
    assert isinstance(ps_out, dict)
    assert "critical_traces" in ps_out

# ====================================================
# PERFORMANCE TIMING BENCHMARK
# ====================================================

def test_explainability_service_performance_large():
    """Asserts ExplainabilityService generates reports under 100ms for large evidence lists."""
    breakdown = ScoreBreakdown(0.5, 0.5, 0.5, 0.5, {})
    # 200 dummy rules factors
    factors = [
        RiskFactor(f"RULE_R{i}", 10.0, "HIGH", "Trigger details", "RULE_ENGINE")
        for i in range(200)
    ]
    hybrid_res = HybridRiskResult("C_LARGE", 0.5, "HIGH", 0.9, breakdown, [], 0.5, factors, "SAR", Explanation("", "", "", ""))
    
    context = ExplainabilityContext(hybrid_result=hybrid_res, evidence_bundle=EvidenceBundle())
    service = ExplainabilityService()
    
    start = time.perf_counter()
    response = service.explain(context)
    duration = (time.perf_counter() - start) * 1000.0
    
    # Should complete well within 100ms
    assert duration < 100.0
