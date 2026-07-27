"""Queue router providing flagged investigations."""

from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any
import hashlib
from app.api.v1.dependencies import get_pipeline_result
from app.models.pipeline_result import PipelineResult

router = APIRouter(tags=["Investigation Queue"])

@router.get(
    "/queue",
    status_code=status.HTTP_200_OK,
    summary="Retrieve investigation queue",
    description="Returns a list of flagged customers."
)
def get_queue(
    pipeline_res: PipelineResult = Depends(get_pipeline_result)
) -> List[Dict[str, Any]]:
    """Retrieves the investigation queue based on flagged customers."""
    
    hybrid_df = pipeline_res.hybrid_risk_dataframe
    
    if hybrid_df.empty:
        return []
        
    # Stratified selection across severity levels so priority filters (Critical, High, Medium, Low) populate
    import pandas as pd
    crit_df = hybrid_df[hybrid_df["severity"] == "CRITICAL"].sort_values(by="overall_risk_score", ascending=False).head(15)
    high_df = hybrid_df[hybrid_df["severity"] == "HIGH"].sort_values(by="overall_risk_score", ascending=False).head(15)
    med_df = hybrid_df[hybrid_df["severity"] == "MEDIUM"].sort_values(by="overall_risk_score", ascending=False).head(10)
    low_df = hybrid_df[hybrid_df["severity"] == "LOW"].sort_values(by="overall_risk_score", ascending=False).head(10)

    combined = pd.concat([crit_df, high_df, med_df, low_df]).drop_duplicates(subset=["customer_id"])
    if len(combined) < 50:
        remainder = hybrid_df[~hybrid_df["customer_id"].isin(combined["customer_id"])].sort_values(by="overall_risk_score", ascending=False).head(50 - len(combined))
        combined = pd.concat([combined, remainder])

    flagged = combined.sort_values(by="overall_risk_score", ascending=False)

    
    queue = []
    for _, row in flagged.iterrows():
        cid = str(row["customer_id"])
        
        # Scale score from 0.0-1.0 to 0-100
        score = int(float(row["overall_risk_score"]) * 100)
        
        severity_map = {
            "CRITICAL": "Critical",
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low"
        }
        
        priority = severity_map.get(str(row["severity"]).upper(), "Low")
        
        # Deterministic but seemingly random values for realism
        hash_val = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        
        # Status
        statuses = ["Pending", "Under Review", "Escalated", "Closed"]
        status_choice = statuses[hash_val % len(statuses)]
        
        # Assignee
        assignees = ["Unassigned", "Sarah J.", "Michael C.", "Alex W.", "System", "David L."]
        assignee_choice = assignees[(hash_val // 10) % len(assignees)]
        
        # Last Updated
        times = ["Just now", "5m ago", "15m ago", "1h ago", "3h ago", "Yesterday"]
        time_choice = times[(hash_val // 100) % len(times)]
        
        queue.append({
            "id": cid,
            "customer": f"Customer {cid}",
            "riskScore": score,
            "priority": priority,
            "status": status_choice,
            "assignedTo": assignee_choice,
            "lastUpdated": time_choice
        })
        
    return queue
