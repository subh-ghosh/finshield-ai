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
            f"| `{e.get('timestamp', '')[:19]}` | **{e.get('action', '')}** | {e.get('description', '')} |"
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

## Analyst Notes

- All findings above are **100% deterministic** and reproducible. Given the same input data, this report will always produce the same output.
- LLM-based narrative generation is available when `GOOGLE_API_KEY` is configured.
- This investigation was completed in **{round(result.execution_time_ms, 1)} ms**.

---
*FinShield AI v2 — Enterprise AML Intelligence Platform*
"""


class ReportGenerator:
    def __init__(self):
        pass

    async def generate(self, result: InvestigationResult) -> str:
        """
        Attempt LLM-based narrative. Falls back to rich deterministic report.
        Per system design: LLMs are ONLY used for natural language presentation.
        The recommendation and risk scores are already locked in before this runs.
        """
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                from langchain_core.prompts import ChatPromptTemplate

                prompt_template = """You are a Senior AML Investigator writing an Executive Summary for a financial crime investigation.

STRICT RULES:
1. Do NOT infer additional facts beyond what is provided.
2. Only summarize the supplied evidence.
3. NEVER modify the recommendation - use it exactly as given.
4. Never invent transactions, customers, or risk scores.
5. Format as professional Markdown.

Structure your report as:
- Executive Summary (2-3 sentences)
- Risk Assessment (use the exact scores provided)
- Key Evidence
- Recommendation & Next Steps

INPUT DATA:
{data}"""

                llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1, google_api_key=api_key)
                prompt = ChatPromptTemplate.from_messages([("system", prompt_template)])

                data_str = json.dumps({
                    "customer_id": result.customer_id,
                    "recommendation": result.recommendation,
                    "risk_score": result.risk_score,
                    "risk_level": result.risk_level,
                    "rule_hits": result.rule_hits,
                    "ml_results": result.ml_results,
                    "evidence_summary": result.evidence_summary,
                    "decision_reasons": result.decision_reasons
                }, indent=2)

                chain = prompt | llm
                response = await chain.ainvoke({"data": data_str})
                return response.content
            except Exception as e:
                # LLM failed — fall through to deterministic
                pass

        # Always-available deterministic report
        return _build_deterministic_report(result)
