"""Deterministic Evidence Gap Detector service evaluating compliance completeness."""

from typing import Dict, Any, List
from app.models.evidence_gap import (
    CompliancePillar,
    EvidenceItemStatus,
    ComplianceItemEvaluation,
    EvidenceGapAssessment
)
from app.orchestrator.models.context import InvestigationContext


class EvidenceGapDetector:
    """Evaluates customer context across 8 compliance pillars to detect missing evidence."""

    def evaluate(self, context: InvestigationContext) -> EvidenceGapAssessment:
        customer_id = context.customer_id
        cust = context.customer_data or {}
        txs = context.transactions or []
        rules = context.rule_hits or []
        evidence = context.evidence or []
        ml_score = context.isolation_forest_score

        evaluations: List[ComplianceItemEvaluation] = []

        # 1. KYC Verification Pillar (Weight: 0.15, Required for SAR)
        kyc_status = str(cust.get("kyc_status", "")).lower()
        has_kyc = bool(cust.get("name") and cust.get("jurisdiction") and kyc_status in ["active", "verified", "completed"])
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.KYC_VERIFICATION,
            name="Customer Identity & KYC Status",
            status=EvidenceItemStatus.PRESENT if has_kyc else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.15,
            is_required_for_sar=True,
            description="Verified PII, active KYC status, and jurisdiction profile.",
            remediation_action="Perform full Customer Due Diligence (CDD) and update identity records."
        ))

        # 2. Source of Funds Pillar (Weight: 0.15, Required for SAR)
        has_sof = float(cust.get("maximum_amount", 0.0)) > 0 or float(cust.get("total_amount", 0.0)) > 0 or len(txs) > 0
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.SOURCE_OF_FUNDS,
            name="Source of Funds & Inflow Analysis",
            status=EvidenceItemStatus.PRESENT if has_sof else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.15,
            is_required_for_sar=True,
            description="Documented origin of incoming capital and transfer funding sources.",
            remediation_action="Request bank statements or proof of wealth documentation from customer."
        ))

        # 3. Beneficial Ownership Pillar (Weight: 0.15, Required for SAR)
        has_ubo = bool(cust.get("industry") and cust.get("industry") != "Unknown")
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.BENEFICIAL_OWNERSHIP,
            name="Ultimate Beneficial Ownership (UBO)",
            status=EvidenceItemStatus.PRESENT if has_ubo else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.15,
            is_required_for_sar=True,
            description="Identified corporate entity structure and control persons.",
            remediation_action="Extract corporate registry records to map beneficial ownership chain."
        ))

        # 4. Transaction Evidence Pillar (Weight: 0.15, Required for SAR)
        has_tx_ev = float(cust.get("transaction_count", 0.0)) > 0 or float(cust.get("rolling_count_24h", 0.0)) > 0 or len(txs) > 0
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.TRANSACTION_EVIDENCE,
            name="Itemized Transaction Audit Trail",
            status=EvidenceItemStatus.PRESENT if has_tx_ev else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.15,
            is_required_for_sar=True,
            description="Chronological log of wire transfers, cash flows, and counterparties.",
            remediation_action="Pull 90-day core banking ledger for entity account."
        ))

        # 5. Network Analysis Pillar (Weight: 0.10, Optional for SAR)
        has_network = float(cust.get("recipient_diversity", 0.0)) > 0 or float(cust.get("sender_diversity", 0.0)) > 0
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.NETWORK_ANALYSIS,
            name="Counterparty Network Risk Analysis",
            status=EvidenceItemStatus.PRESENT if has_network else EvidenceItemStatus.MISSING_OPTIONAL,
            weight=0.10,
            is_required_for_sar=False,
            description="Graph connectivity and counterparty risk scoring.",
            remediation_action="Run 2-hop network traversal on high-risk counterparties."
        ))

        # 6. Rule Engine Validation Pillar (Weight: 0.10, Required for SAR)
        has_rules = len(rules) > 0 or context.hybrid_risk_score > 0.35
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.RULE_VALIDATION,
            name="Deterministic Rule Trigger Evaluation",
            status=EvidenceItemStatus.PRESENT if has_rules else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.10,
            is_required_for_sar=True,
            description="Evaluated AML rule indicators and threshold breaches.",
            remediation_action="Execute full AML Rule Engine check against transaction history."
        ))

        # 7. External Verification & ML Anomaly Pillar (Weight: 0.10, Optional for SAR)
        has_ml = ml_score > 0.0
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.EXTERNAL_VERIFICATION,
            name="Isolation Forest Anomaly & Watchlist Screening",
            status=EvidenceItemStatus.PRESENT if has_ml else EvidenceItemStatus.MISSING_OPTIONAL,
            weight=0.10,
            is_required_for_sar=False,
            description="Machine learning outlier score and external database cross-referencing.",
            remediation_action="Trigger Isolation Forest anomaly detection and PEP screening."
        ))

        # 8. Analyst Notes & Timeline Audit Pillar (Weight: 0.10, Required for SAR)
        has_notes = len(evidence) > 0 or len(context.timeline) > 0
        evaluations.append(ComplianceItemEvaluation(
            pillar=CompliancePillar.ANALYST_NOTES,
            name="Investigator Disposition & Audit Log",
            status=EvidenceItemStatus.PRESENT if has_notes else EvidenceItemStatus.MISSING_CRITICAL,
            weight=0.10,
            is_required_for_sar=True,
            description="Documented rationale, evidence aggregation, and audit trail.",
            remediation_action="Record investigator decision notes in case file."
        ))

        # Calculate Completeness Score
        total_weight = sum(ev.weight for ev in evaluations)
        passed_weight = sum(ev.weight for ev in evaluations if ev.status == EvidenceItemStatus.PRESENT)
        completeness_score = round((passed_weight / total_weight) * 100.0, 1) if total_weight > 0 else 0.0

        # Categorize gaps
        missing_critical = [ev.name for ev in evaluations if ev.status == EvidenceItemStatus.MISSING_CRITICAL]
        missing_optional = [ev.name for ev in evaluations if ev.status == EvidenceItemStatus.MISSING_OPTIONAL]
        
        # Determine SAR Filing Readiness (Requires >= 75% completeness and 0 blocking critical gaps)
        blocking_critical_gaps_count = sum(1 for ev in evaluations if ev.status == EvidenceItemStatus.MISSING_CRITICAL and ev.is_required_for_sar)
        sar_filing_ready = (completeness_score >= 75.0) and (blocking_critical_gaps_count == 0)

        warnings: List[str] = []
        if blocking_critical_gaps_count > 0:
            warnings.append(f"Filing Blocked: {blocking_critical_gaps_count} critical mandatory evidence item(s) are missing.")
        if completeness_score < 75.0:
            warnings.append(f"Low Completeness: Investigation completeness ({completeness_score}%) is below 75% regulatory threshold.")

        remediation_roadmap = [ev.remediation_action for ev in evaluations if ev.status != EvidenceItemStatus.PRESENT]

        return EvidenceGapAssessment(
            customer_id=customer_id,
            completeness_score=completeness_score,
            sar_filing_ready=sar_filing_ready,
            blocking_critical_gaps_count=blocking_critical_gaps_count,
            total_items_evaluated=len(evaluations),
            passed_items_count=sum(1 for ev in evaluations if ev.status == EvidenceItemStatus.PRESENT),
            evaluations=evaluations,
            warnings=warnings,
            missing_critical_items=missing_critical,
            missing_optional_items=missing_optional,
            remediation_roadmap=remediation_roadmap
        )
