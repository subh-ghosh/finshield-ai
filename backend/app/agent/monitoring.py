"""Monitoring Agent — Continuous case lifecycle management."""
import json
from datetime import datetime
from typing import Dict, List, Set

class MonitoringAgent:
    """Tracks investigated customers and flags re-emerging risk."""
    
    def __init__(self):
        self._watchlist: Dict[str, dict] = {
            "C_1204": {
                "risk_level": "HIGH",
                "priority": "High",
                "evidence_count": 3,
                "added_at": datetime.utcnow().isoformat(),
                "last_checked": datetime.utcnow().isoformat(),
                "status": "MONITORING",
                "reopen_count": 0,
                "reason": "Multiple offshore wire transfers flagged"
            },
            "C_9358": {
                "risk_level": "CRITICAL",
                "priority": "Critical",
                "evidence_count": 5,
                "added_at": datetime.utcnow().isoformat(),
                "last_checked": datetime.utcnow().isoformat(),
                "status": "ESCALATED",
                "reopen_count": 1,
                "reason": "Velocity limits exceeded and shell company matches"
            },
            "C_4301": {
                "risk_level": "MEDIUM",
                "priority": "Medium",
                "evidence_count": 1,
                "added_at": datetime.utcnow().isoformat(),
                "last_checked": datetime.utcnow().isoformat(),
                "status": "MONITORING",
                "reopen_count": 0,
                "reason": "Sudden change in transaction behavior"
            }
        }  # customer_id → {risk_level, last_checked, ...}
    
    def add_to_watchlist(self, customer_id: str, risk_level: str, evidence_count: int):
        self._watchlist[customer_id] = {
            "risk_level": risk_level,
            "evidence_count": evidence_count,
            "added_at": datetime.utcnow().isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "status": "MONITORING",
            "reopen_count": 0
        }
    
    def check_customer(self, customer_id: str, current_risk: float) -> dict:
        """Check if a monitored customer's risk has changed."""
        if customer_id not in self._watchlist:
            return {"action": "NONE"}
        
        entry = self._watchlist[customer_id]
        entry["last_checked"] = datetime.utcnow().isoformat()
        
        if current_risk > 75 and entry["risk_level"] in ["LOW", "MEDIUM"]:
            entry["status"] = "ESCALATED"
            entry["reopen_count"] += 1
            return {"action": "REOPEN", "reason": f"Risk escalated from {entry['risk_level']} to HIGH"}
        
        return {"action": "CONTINUE_MONITORING"}
    
    def get_watchlist(self) -> List[dict]:
        return [{"customer_id": k, **v} for k, v in self._watchlist.items()]

# Global instance for singleton-like usage in this prototype
monitoring_agent_instance = MonitoringAgent()
