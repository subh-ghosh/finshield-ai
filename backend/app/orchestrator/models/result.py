from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class InvestigationResult(BaseModel):
    customer_id: str
    correlation_id: str
    execution_time_ms: float
    
    recommendation: str
    risk_score: float
    risk_level: str
    confidence: float
    
    rule_hits: List[Dict[str, Any]]
    ml_results: Dict[str, Any]
    evidence_summary: List[str]
    timeline: List[Dict[str, Any]]
    decision_reasons: List[str]
    
    executive_summary: Optional[str] = None
    investigation_narrative: Optional[str] = None
