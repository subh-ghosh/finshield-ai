from typing import Dict, Any, List
from pydantic import BaseModel, Field
import time
from datetime import datetime
class InvestigationContext(BaseModel):
    customer_id: str
    correlation_id: str
    start_time: float = Field(default_factory=time.time)
    customer_data: Dict[str, Any] = Field(default_factory=dict)
    transactions: List[Dict[str, Any]] = Field(default_factory=list)
    features: Dict[str, Any] = Field(default_factory=dict)
    rule_hits: List[Dict[str, Any]] = Field(default_factory=list)
    isolation_forest_score: float = 0.0
    hybrid_risk_score: float = 0.0
    evidence: List[str] = Field(default_factory=list)
    timeline: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_timeline_event(self, action: str, description: str):
        self.timeline.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action, 
            "description": description
        })
