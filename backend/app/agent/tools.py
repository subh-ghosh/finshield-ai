import pandas as pd
import time
import json
import os
from typing import Dict, List, Any

# --- Global Dataset Loading ---
# We load the dataset once at module initialization to ensure fast API responses.
# Determine base directory dynamically to support both local dev and Docker
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

# Use environment variable if running inside Docker
if os.environ.get("DOCKER_ENV"):
    DATASET_DIR = "/app/dataset"

ACCOUNTS_PATH = os.path.join(DATASET_DIR, "accounts.csv")
TRANSACTIONS_PATH = os.path.join(DATASET_DIR, "transactions.csv")
ALERTS_PATH = os.path.join(DATASET_DIR, "alerts.csv")

try:
    print("Loading IBM AML Dataset into memory (capped for cloud free tier)...")
    # accounts.csv: load needed columns to save memory
    df_accounts = pd.read_csv(ACCOUNTS_PATH, usecols=["ACCOUNT_ID", "CUSTOMER_ID", "INIT_BALANCE", "COUNTRY", "IS_FRAUD"], nrows=5000)
    # transactions.csv: limit to 5k rows to fit in 512MB Render free tier
    df_transactions = pd.read_csv(TRANSACTIONS_PATH, nrows=5000)
    # alerts.csv: load fully (it's small ~88KB)
    df_alerts = pd.read_csv(ALERTS_PATH)
    print(f"Dataset loaded: {len(df_accounts)} accounts, {len(df_transactions)} transactions, {len(df_alerts)} alerts.")
except Exception as e:
    print(f"Error loading dataset: {e}")
    df_accounts = pd.DataFrame()
    df_transactions = pd.DataFrame()
    df_alerts = pd.DataFrame()

from langchain_core.tools import tool

def _get_account_id(customer_id: str) -> int:
    """Helper to map customer_id (e.g. C_1) to numeric ACCOUNT_ID"""
    try:
        if customer_id.upper().startswith("C_"):
            num = int(customer_id.split("_")[1])
        else:
            num = int(customer_id)
        return num
    except:
        return -1

@tool
def customer_360_tool(customer_id: str) -> str:
    """Retrieve complete profile and historical risk for a customer from accounts.csv."""
    time.sleep(0.1)
    account_id = _get_account_id(customer_id)
    if df_accounts.empty:
        return json.dumps({"status": "error", "data": "Dataset not loaded."})
    
    account_data = df_accounts[df_accounts["ACCOUNT_ID"] == account_id]
    if account_data.empty:
        return json.dumps({"status": "success", "data": f"Customer {customer_id} not found in accounts dataset."})
    
    row = account_data.iloc[0]
    country = row.get("COUNTRY", "Unknown")
    acct_type = row.get("ACCOUNT_TYPE", "Unknown")
    balance = row.get("INIT_BALANCE", 0.0)
    is_fraud = row.get("IS_FRAUD", False)
    
    risk_level = "High risk profile" if is_fraud else "Normal profile"
    
    return json.dumps({
        "status": "success",
        "data": f"Customer {customer_id}: {risk_level}. Account Type: {acct_type}. Country: {country}. Initial Balance: ${balance:,.2f}."
    })

@tool
def transaction_tool(customer_id: str) -> str:
    """Retrieve transaction volumes and velocities from transactions.csv."""
    time.sleep(0.1)
    account_id = _get_account_id(customer_id)
    if df_transactions.empty:
        return json.dumps({"status": "error", "data": "Dataset not loaded."})
    
    # Transactions where customer is sender or receiver
    tx_data = df_transactions[(df_transactions["SENDER_ACCOUNT_ID"] == account_id) | (df_transactions["RECEIVER_ACCOUNT_ID"] == account_id)]
    
    tx_count = len(tx_data)
    if tx_count == 0:
        return json.dumps({"status": "success", "data": f"No transactions found for Customer {customer_id}."})
    
    total_volume = tx_data["TX_AMOUNT"].sum()
    avg_tx = tx_data["TX_AMOUNT"].mean()
    
    return json.dumps({
        "status": "success",
        "data": f"Recent transactions for {customer_id}: {tx_count} transactions found. Total volume: ${total_volume:,.2f}. Average size: ${avg_tx:,.2f}."
    })

@tool
def rule_engine_tool(customer_id: str) -> str:
    """Run AML deterministic rules against the customer using live Pipeline results."""
    time.sleep(0.1)
    
    if customer_id not in pipeline_result_cache:
        return json.dumps({"status": "error", "data": "Pipeline results not found. Ensure pipeline has run."})
        
    pipeline_res = pipeline_result_cache[customer_id]
    rule_map = {res.customer_id: res for res in pipeline_res.rule_analysis}
    
    if customer_id not in rule_map or not getattr(rule_map[customer_id], "triggered_rules", []):
        return json.dumps({"status": "success", "data": "Rule Engine Output: No deterministic rules triggered. Customer behavior is normal."})
    
    triggers = []
    for r in getattr(rule_map[customer_id], "triggered_rules", []):
        triggers.append(f"- {getattr(r, 'rule_name', str(r)).upper()} Network Pattern: TRIGGERED ({getattr(r, 'description', '')})")
        
    return json.dumps({
        "status": "success",
        "data": f"Rule Engine Output: \n" + "\n".join(triggers)
    })

@tool
def isolation_forest_tool(customer_id: str) -> str:
    """Run anomaly detection dynamically based on the live ML Pipeline Isolation Forest score."""
    time.sleep(0.1)
    
    if customer_id not in pipeline_result_cache:
        return json.dumps({"status": "error", "data": "Pipeline results not found. Ensure pipeline has run."})
        
    pipeline_res = pipeline_result_cache[customer_id]
    anom_map = {res.customer_id: res for res in pipeline_res.anomaly_analysis}
    
    if customer_id not in anom_map:
        return json.dumps({
            "status": "success",
            "data": "Isolation Forest Output: Normal baseline behavior. No ML anomalies detected."
        })
        
    anom_res = anom_map[customer_id]
    anomaly_score = round(float(getattr(anom_res, "anomaly_score", 0.0)), 4)
    desc = getattr(anom_res, "description", getattr(anom_res, "severity", "Unknown severity"))
    
    return json.dumps({
        "status": "success",
        "data": f"Isolation Forest Output: Anomaly Score: {anomaly_score} ({desc})."
    })

@tool
def hybrid_risk_tool(customer_id: str) -> str:
    """Run Hybrid Risk Engine combining actual rules and ML scores."""
    time.sleep(0.1)
    
    try:
        from app.api.v1.dependencies import get_pipeline_result
        pipeline_res = get_pipeline_result()
        if pipeline_res and pipeline_res.hybrid_risk_analysis:
            hybrid_map = {res.customer_id: res for res in pipeline_res.hybrid_risk_analysis}
            h_res = hybrid_map.get(customer_id)
            if h_res:
                score = h_res.overall_risk_score * 100
                if score >= 85:
                    return json.dumps({"status": "success", "data": f"Hybrid Risk Output: CRITICAL Risk (Score: {score:.1f}). Verified network alerts combined with high ML anomaly score strongly indicates layering."})
                elif score >= 65:
                    return json.dumps({"status": "success", "data": f"Hybrid Risk Output: HIGH Risk (Score: {score:.1f}). Significant indicators found by either rules or ML models."})
                elif score >= 35:
                    return json.dumps({"status": "success", "data": f"Hybrid Risk Output: MEDIUM Risk (Score: {score:.1f}). Moderate activity requiring further manual review."})
                else:
                    return json.dumps({"status": "success", "data": f"Hybrid Risk Output: LOW Risk (Score: {score:.1f}). Entity activity aligns with expected behavioral baseline."})
    except Exception as e:
        print(f"Error accessing pipeline result in hybrid risk tool: {e}")
        pass
        
    return json.dumps({"status": "success", "data": "Hybrid Risk Output: LOW Risk (Score: 0.0). No risk data found."})

@tool
def timeline_tool(customer_id: str) -> str:
    """Construct a chronological timeline from real transactions."""
    time.sleep(0.1)
    account_id = _get_account_id(customer_id)
    if df_transactions.empty:
        return json.dumps({"status": "error", "data": "Dataset not loaded."})
        
    tx_data = df_transactions[(df_transactions["SENDER_ACCOUNT_ID"] == account_id) | (df_transactions["RECEIVER_ACCOUNT_ID"] == account_id)].head(5)
    
    if tx_data.empty:
        return json.dumps({"status": "success", "data": f"Timeline: No events found for Customer {customer_id}."})
        
    timeline_str = "Timeline:\n"
    for _, row in tx_data.iterrows():
        is_sender = (row["SENDER_ACCOUNT_ID"] == account_id)
        direction = "SENT" if is_sender else "RECEIVED"
        counterparty = row["RECEIVER_ACCOUNT_ID"] if is_sender else row["SENDER_ACCOUNT_ID"]
        timeline_str += f"- Timestamp {row['TIMESTAMP']}: {direction} ${row['TX_AMOUNT']:,.2f} (Counterparty Account {counterparty})\n"
        
    return json.dumps({
        "status": "success",
        "data": timeline_str
    })


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
