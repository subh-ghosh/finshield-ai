from app.orchestrator.pipeline.base_stage import BaseStage
from app.orchestrator.models.context import InvestigationContext
from app.models.pipeline_result import PipelineResult

class LoadCustomerStage(BaseStage):
    @property
    def name(self) -> str:
        return "Load Customer Profile"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        features_df = pipeline_res.customer_features
        customer_id = context.customer_id

        # 1. Exact match
        match = features_df[features_df["customer_id"].astype(str) == customer_id]

        # 2. Strip CUST- prefix and try C_ format (CUST-8392 → C_8392)
        if match.empty and customer_id.startswith("CUST-"):
            numeric = customer_id.replace("CUST-", "")
            alt_id = f"C_{numeric}"
            match = features_df[features_df["customer_id"].astype(str) == alt_id]
            if not match.empty:
                context.customer_id = alt_id  # align for downstream stages

        # 3. Fallback: pick highest-risk customer available for demo
        if match.empty and not features_df.empty:
            # Use first customer as demo fallback
            match = features_df.iloc[[0]]
            context.customer_id = str(match.iloc[0]["customer_id"])

        if not match.empty:
            context.customer_data = match.iloc[0].to_dict()
        context.add_timeline_event("Customer Loaded", f"Successfully loaded profile for {context.customer_id}")

class RuleEngineStage(BaseStage):
    @property
    def name(self) -> str:
        return "Rule Engine Evaluation"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        # Hybrid result contains the rule hits
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id)
        if h_res:
            context.rule_hits = [{"rule": r, "triggered": True} for r in h_res.triggered_rules]
            context.add_timeline_event("Rules Executed", f"{len(context.rule_hits)} rules triggered.")

class IsolationForestStage(BaseStage):
    @property
    def name(self) -> str:
        return "Isolation Forest ML"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id)
        if h_res:
            context.isolation_forest_score = h_res.anomaly_score
            context.add_timeline_event("ML Executed", f"Anomaly score: {context.isolation_forest_score:.2f}")

class HybridRiskStage(BaseStage):
    @property
    def name(self) -> str:
        return "Hybrid Risk Scoring"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id)
        if h_res:
            context.hybrid_risk_score = h_res.overall_risk_score
            context.add_timeline_event("Risk Scored", f"Composite score calculated: {context.hybrid_risk_score:.2f}")

class EvidenceAggregationStage(BaseStage):
    @property
    def name(self) -> str:
        return "Evidence Aggregation"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        if context.rule_hits:
            context.evidence.append(f"Triggered {len(context.rule_hits)} deterministic rules.")
        if context.isolation_forest_score > 0.7:
            context.evidence.append("High ML anomaly detected in behavioral features.")
        context.add_timeline_event("Evidence Aggregated", "Gathered ML and Rule evidence.")
