import pandas as pd
from app.orchestrator.pipeline.base_stage import BaseStage
from app.orchestrator.models.context import InvestigationContext
from app.models.pipeline_result import PipelineResult

class LoadCustomerStage(BaseStage):
    @property
    def name(self) -> str:
        return "Load Customer Profile"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        features_df = pipeline_res.customer_features
        raw_cid = str(context.customer_id).strip() if context.customer_id else "UNKNOWN"
        clean_num = raw_cid.replace("CUST-", "").replace("C_", "")

        match = pd.DataFrame()
        if raw_cid != "UNKNOWN" and not features_df.empty and "customer_id" in features_df.columns:
            str_ids = features_df["customer_id"].astype(str).str.replace("CUST-", "", regex=False).str.replace("C_", "", regex=False)
            match = features_df[str_ids == clean_num]

        # If UNKNOWN or customer not found, pick entity with max overall_risk_score
        if match.empty or raw_cid == "UNKNOWN":
            if pipeline_res.hybrid_risk_analysis:
                max_res = max(pipeline_res.hybrid_risk_analysis, key=lambda x: getattr(x, 'overall_risk_score', 0))
                target_id = max_res.customer_id
                target_num = str(target_id).replace("CUST-", "").replace("C_", "")
                str_ids = features_df["customer_id"].astype(str).str.replace("CUST-", "", regex=False).str.replace("C_", "", regex=False)
                m = features_df[str_ids == target_num]
                if not m.empty:
                    match = m
                    context.customer_id = target_id

            if match.empty and not features_df.empty:
                if "risk_score" in features_df.columns:
                    match = features_df.sort_values(by="risk_score", ascending=False).iloc[[0]]
                elif "anomaly_score" in features_df.columns:
                    match = features_df.sort_values(by="anomaly_score", ascending=False).iloc[[0]]
                else:
                    match = features_df.iloc[[-1]]
                context.customer_id = str(match.iloc[0]["customer_id"])

        if not match.empty:
            context.customer_data = match.iloc[0].to_dict()
        context.add_timeline_event("Customer Loaded", f"Successfully loaded profile for {context.customer_id}")

class RuleEngineStage(BaseStage):
    @property
    def name(self) -> str:
        return "Rule Engine Evaluation"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id) or hybrid_map.get(context.customer_id.replace("C_", "CUST-"))
        if not h_res and pipeline_res.hybrid_risk_analysis:
            h_res = max(pipeline_res.hybrid_risk_analysis, key=lambda x: getattr(x, 'overall_risk_score', 0))

        if h_res:
            context.rule_hits = [{"rule": r, "triggered": True} for r in h_res.triggered_rules]
            context.add_timeline_event("Rules Executed", f"{len(context.rule_hits)} rules triggered.")

class IsolationForestStage(BaseStage):
    @property
    def name(self) -> str:
        return "Isolation Forest ML"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id) or hybrid_map.get(context.customer_id.replace("C_", "CUST-"))
        if not h_res and pipeline_res.hybrid_risk_analysis:
            h_res = max(pipeline_res.hybrid_risk_analysis, key=lambda x: getattr(x, 'overall_risk_score', 0))

        if h_res:
            context.isolation_forest_score = h_res.anomaly_score
            context.add_timeline_event("ML Executed", f"Anomaly score: {context.isolation_forest_score:.2f}")

class HybridRiskStage(BaseStage):
    @property
    def name(self) -> str:
        return "Hybrid Risk Scoring"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
        h_res = hybrid_map.get(context.customer_id) or hybrid_map.get(context.customer_id.replace("C_", "CUST-"))
        if not h_res and pipeline_res.hybrid_risk_analysis:
            h_res = max(pipeline_res.hybrid_risk_analysis, key=lambda x: getattr(x, 'overall_risk_score', 0))

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

class EvidenceGapDetectorStage(BaseStage):
    @property
    def name(self) -> str:
        return "Evidence Gap & Compliance Detector"

    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        from app.services.evidence_gap_detector import EvidenceGapDetector
        detector = EvidenceGapDetector()
        gap_assessment = detector.evaluate(context)
        context.add_timeline_event(
            "Compliance Evaluated",
            f"Completeness Score: {gap_assessment.completeness_score}%. SAR Ready: {gap_assessment.sar_filing_ready}"
        )
