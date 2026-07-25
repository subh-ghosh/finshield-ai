from langchain_core.tools import tool
import time
import json


@tool
def customer_360_tool(customer_id: str) -> str:
    """Retrieve complete profile and historical risk for a customer."""
    time.sleep(0.5)
    return json.dumps(
        {
            "status": "success",
            "data": f"Customer {customer_id}: High risk profile (92/100). KYC verified. Industry: Import/Export. Jurisdiction: Cayman Islands.",
        }
    )


@tool
def transaction_tool(customer_id: str) -> str:
    """Retrieve recent transactions and velocity scores."""
    time.sleep(0.5)
    return json.dumps(
        {
            "status": "success",
            "data": f"Recent transactions for {customer_id}: 145 transactions in 7 days. High velocity detected. Total volume: $1.2M USD.",
        }
    )


@tool
def rule_engine_tool(customer_id: str) -> str:
    """Run AML deterministic rules against the customer."""
    time.sleep(1)
    return json.dumps(
        {
            "status": "success",
            "data": "Rule Engine Output: \n- Structuring Pattern (Rule-004): TRIGGERED\n- High Risk Jurisdiction (Rule-012): TRIGGERED",
        }
    )


@tool
def isolation_forest_tool(customer_id: str) -> str:
    """Run unsupervised anomaly detection using Isolation Forest."""
    time.sleep(1.5)
    return json.dumps(
        {
            "status": "success",
            "data": "Isolation Forest Output: Anomaly Score: 0.89 (Top 1% anomalous). Cluster distance indicates highly unusual wire transfer behavior.",
        }
    )


@tool
def hybrid_risk_tool(customer_id: str) -> str:
    """Run Hybrid Risk Engine combining rules and ML scores."""
    time.sleep(0.5)
    return json.dumps(
        {
            "status": "success",
            "data": "Hybrid Risk Output: Critical Risk. The combination of Rule-004 (Structuring) and ML Anomaly Score (0.89) strongly indicates layering.",
        }
    )


@tool
def timeline_tool(customer_id: str) -> str:
    """Construct a chronological timeline of events for the customer."""
    time.sleep(0.5)
    return json.dumps(
        {
            "status": "success",
            "data": "Timeline:\n- Day 1: Account opened via offshore entity.\n- Day 3: $500k received from unknown third party.\n- Day 4-7: 145 small transfers just below reporting thresholds ($9.9k).",
        }
    )


TOOLS = [
    customer_360_tool,
    transaction_tool,
    rule_engine_tool,
    isolation_forest_tool,
    hybrid_risk_tool,
    timeline_tool,
]


def get_tool_by_name(name: str):
    for t in TOOLS:
        if t.name == name:
            return t
    return None
