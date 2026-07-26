"""
AML Investigation Report Generator.
Attempts LLM-based narrative generation; falls back to rich deterministic report.
"""
import os
import json
from datetime import datetime
from app.orchestrator.models.result import InvestigationResult


def _build_deterministic_report(result: InvestigationResult) -> str:
    """Generate a structured professional markdown report from deterministic data."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    risk_pct = round(result.risk_score * 100, 1)
    
    # Status indicators (ASCII-safe for all terminals)
    rec_icons = {
        "FILE_SAR": "[CRITICAL]",
        "ESCALATE": "[HIGH]",
        "MANUAL_REVIEW": "[MEDIUM]",
        "CLEAR": "[CLEAR]",
    }
    icon = rec_icons.get(result.recommendation, "[UNKNOWN]")

    rule_hits_md = ""
    if result.rule_hits:
        rules = [f"- `{r.get('rule', r)}` — **Triggered**" for r in result.rule_hits]
        rule_hits_md = "\n".join(rules)
    else:
        rule_hits_md = "_No deterministic rules triggered._"

    evidence_md = ""
    if result.evidence_summary:
        evidence_md = "\n".join(f"- {e}" for e in result.evidence_summary)
    else:
        evidence_md = "_No significant evidence flags detected._"

    reasons_md = "\n".join(f"{i+1}. {r}" for i, r in enumerate(result.decision_reasons))

    timeline_md = ""
    if result.timeline:
        timeline_md = "\n".join(
            f"| `{e.get('timestamp', '')[:19].replace('T', ' ')}` | **{e.get('action', '')}** | {e.get('description', '')} |"
            for e in result.timeline
        )
    
    ml_score = result.ml_results.get("isolation_forest_score", 0.0)
    ml_label = "HIGH" if ml_score > 0.7 else ("MEDIUM" if ml_score > 0.4 else "LOW")

    return f"""# FinShield AI — AML Investigation Report

**Generated:** {now}  
**Customer ID:** `{result.customer_id}`  
**Correlation ID:** `{result.correlation_id}`  
**Engine Version:** v2.0.0 (Deterministic)

---

## Executive Summary

This report presents the findings of an automated Anti-Money Laundering (AML) investigation
conducted by the FinShield AI v2 deterministic investigation engine. The analysis evaluated
customer `{result.customer_id}` across multiple risk dimensions including rule-based detection,
machine learning anomaly scoring, and hybrid risk fusion.

> **Recommendation: {icon} {result.recommendation}**  
> **Risk Level:** {result.risk_level} | **Risk Score:** {risk_pct}/100 | **Confidence:** {round(result.confidence * 100)}%

---

## Deterministic Findings

### Risk Score Breakdown

| Dimension | Score | Label |
|-----------|-------|-------|
| **Hybrid Composite Risk** | {risk_pct}% | {result.risk_level} |
| **ML Anomaly (Isolation Forest)** | {round(ml_score * 100, 1)}% | {ml_label} |
| **Rule Engine Hits** | {len(result.rule_hits)} rules | {"FLAGGED" if result.rule_hits else "CLEAR"} |

### Decision Rationale

{reasons_md}

---

## Rule Engine Results

{rule_hits_md}

---

## Key Evidence

{evidence_md}

---

## Investigation Timeline

| Timestamp | Stage | Details |
|-----------|-------|---------|
{timeline_md}

---
*FinShield AI v2 — Enterprise AML Intelligence Platform*
"""


class ReportGenerator:
    def __init__(self):
        pass

    async def generate(self, result: InvestigationResult) -> str:
        """
        Generates a rich deterministic markdown report without relying on LLMs.
        """
        return _build_deterministic_report(result)
