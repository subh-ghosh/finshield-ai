import time
import uuid
import yaml
from app.orchestrator.models.context import InvestigationContext
from app.orchestrator.models.result import InvestigationResult
from app.orchestrator.decision.decision_engine import DecisionEngine
from app.orchestrator.report.generator import ReportGenerator
from app.models.pipeline_result import PipelineResult

from app.orchestrator.pipeline.stages import (
    LoadCustomerStage,
    RuleEngineStage,
    IsolationForestStage,
    HybridRiskStage,
    EvidenceAggregationStage
)

STAGE_REGISTRY = {
    "LoadCustomerStage": LoadCustomerStage,
    "RuleEngineStage": RuleEngineStage,
    "IsolationForestStage": IsolationForestStage,
    "HybridRiskStage": HybridRiskStage,
    "EvidenceAggregationStage": EvidenceAggregationStage
}

class InvestigationOrchestrator:
    def __init__(self, config_path: str = "app/orchestrator/config/pipeline.yaml"):
        self.stages = []
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                stage_names = config.get("stages", [])
                for name in stage_names:
                    if name in STAGE_REGISTRY:
                        self.stages.append(STAGE_REGISTRY[name]())
        except Exception:
            # Fallback
            self.stages = [
                LoadCustomerStage(),
                RuleEngineStage(),
                IsolationForestStage(),
                HybridRiskStage(),
                EvidenceAggregationStage()
            ]
        self.decision_engine = DecisionEngine()
        self.report_generator = ReportGenerator()

    async def investigate(self, customer_id: str, pipeline_res: PipelineResult, user_request: str = "") -> InvestigationResult:
        correlation_id = str(uuid.uuid4())
        context = InvestigationContext(customer_id=customer_id, correlation_id=correlation_id)
        
        # Execute Pipeline
        for stage in self.stages:
            await stage.execute(context, pipeline_res)
            
        # Decision
        decision = self.decision_engine.evaluate(context)
        
        # Build deterministic result
        result = InvestigationResult(
            customer_id=context.customer_id,
            correlation_id=correlation_id,
            execution_time_ms=(time.time() - context.start_time) * 1000,
            recommendation=decision["recommendation"],
            risk_score=context.hybrid_risk_score,
            risk_level=decision["risk_level"],
            confidence=decision["confidence"],
            rule_hits=context.rule_hits,
            ml_results={"isolation_forest_score": context.isolation_forest_score},
            evidence_summary=context.evidence,
            timeline=context.timeline,
            decision_reasons=decision["decision_reasons"]
        )
        
        # Generate LLM Report
        report_md = await self.report_generator.generate(result, user_req=user_request)
        result.executive_summary = report_md
        
        return result
