"""Configuration settings for explainability templates, severity rules, and formatting."""

# Natural language investigator templates classified by severity levels
EXPLANATION_TEMPLATES: dict = {
    "LOW": {
        "summary": "Customer {customer_id} exhibits a low threat signature. Checked metrics reside within normal operating bounds. Continued automated monitoring is recommended.",
        "findings": "Zero critical indicators triggered. Transaction patterns match normal profile."
    },
    "MEDIUM": {
        "summary": "Customer {customer_id} exhibits a medium threat signature. Elevated indicators detected: {rules_summary}. Behavioral signals show moderate variance: {behavior_summary}. Isolation Forest outlier classification: {ml_summary}. Manual verification is recommended.",
        "findings": "Triggered violations: {rules_list}. Outlier score: {ml_score:.4f}."
    },
    "HIGH": {
        "summary": "Customer {customer_id} exhibits a high threat signature. Multiple severe violations triggered: {rules_summary}. Behavioral traits show high variance: {behavior_summary}. ML model confirms outlier state with score {ml_score:.4f}. Immediate escalation is recommended.",
        "findings": "Critical violations: {rules_list}. Outlier score: {ml_score:.4f}."
    },
    "CRITICAL": {
        "summary": "Customer {customer_id} exhibits a critical threat signature. Urgent security incident. Major violations triggered: {rules_summary}. Outlier model shows maximum deviation: {ml_score:.4f}. Prompt case filing (SAR) recommended.",
        "findings": "Violations: {rules_list}. Outlier score: {ml_score:.4f}."
    }
}
