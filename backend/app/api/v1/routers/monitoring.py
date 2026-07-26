from fastapi import APIRouter
from app.agent.monitoring import monitoring_agent_instance

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/watchlist")
def get_watchlist():
    return monitoring_agent_instance.get_watchlist()

@router.post("/check/{customer_id}")
def check_customer(customer_id: str, current_risk: float):
    return monitoring_agent_instance.check_customer(customer_id, current_risk)
