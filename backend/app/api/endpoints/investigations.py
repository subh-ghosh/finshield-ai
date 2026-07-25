from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()


class CustomerModel(BaseModel):
    id: str
    name: str
    risk_score: int
    priority: str
    status: str
    assigned_analyst: str
    recent_transactions: int


@router.get("/queue", response_model=List[CustomerModel])
def get_investigation_queue():
    # Mock data for the investigation queue
    return [
        {
            "id": "CUST-8392",
            "name": "Acme Corp Ltd",
            "risk_score": 92,
            "priority": "Critical",
            "status": "Open",
            "assigned_analyst": "Unassigned",
            "recent_transactions": 145,
        },
        {
            "id": "CUST-1042",
            "name": "Global Traders Inc",
            "risk_score": 85,
            "priority": "High",
            "status": "In Progress",
            "assigned_analyst": "Sarah Jenkins",
            "recent_transactions": 89,
        },
        {
            "id": "CUST-4491",
            "name": "TechVentures LLC",
            "risk_score": 78,
            "priority": "High",
            "status": "Open",
            "assigned_analyst": "Unassigned",
            "recent_transactions": 34,
        },
        {
            "id": "CUST-9921",
            "name": "Nexus Dynamics",
            "risk_score": 65,
            "priority": "Medium",
            "status": "In Progress",
            "assigned_analyst": "Michael Chen",
            "recent_transactions": 12,
        },
    ]


@router.get("/dashboard/stats")
def get_dashboard_stats():
    return {
        "active_investigations": 124,
        "high_risk_customers": 38,
        "new_alerts": 15,
        "pending_reviews": 42,
    }


@router.get("/dashboard/risk-distribution")
def get_risk_distribution():
    return [
        {"name": "Low (0-30)", "value": 450, "fill": "#3b82f6"},
        {"name": "Medium (31-60)", "value": 320, "fill": "#eab308"},
        {"name": "High (61-80)", "value": 150, "fill": "#f97316"},
        {"name": "Critical (81-100)", "value": 38, "fill": "#ef4444"},
    ]


@router.get("/dashboard/anomaly-trend")
def get_anomaly_trend():
    return [
        {"time": "00:00", "anomalies": 12},
        {"time": "04:00", "anomalies": 8},
        {"time": "08:00", "anomalies": 35},
        {"time": "12:00", "anomalies": 42},
        {"time": "16:00", "anomalies": 38},
        {"time": "20:00", "anomalies": 15},
    ]


@router.get("/{customer_id}")
def get_customer_details(customer_id: str):
    # Base mock profile
    return {
        "id": customer_id,
        "name": (
            "Acme Corp Ltd" if customer_id == "CUST-8392" else f"Customer {customer_id}"
        ),
        "kyc_status": "Verified",
        "risk_score": 92,
        "onboarding_date": "2023-01-15",
        "industry": "Import/Export",
        "jurisdiction": "Cayman Islands",
        "historical_risk": "Medium",
        "connected_customers": [
            {
                "id": "CUST-1042",
                "name": "Global Traders Inc",
                "relation": "Shared Director",
            },
            {
                "id": "CUST-5512",
                "name": "Offshore Holdings",
                "relation": "Parent Company",
            },
        ],
    }
