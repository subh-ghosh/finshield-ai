"""Aggregated APIRouter for API v1 combining analysis, customer, health, metrics, and planner modules."""

from fastapi import APIRouter
from app.api.v1.routers.analysis import router as analysis_router
from app.api.v1.routers.customer import router as customer_router
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.metrics import router as metrics_router
from app.api.v1.routers.planner import router as planner_router
from app.api.v1.routers.queue import router as queue_router

v1_router = APIRouter()

# Include sub-routers
v1_router.include_router(analysis_router)
v1_router.include_router(customer_router)
v1_router.include_router(health_router)
v1_router.include_router(metrics_router)
v1_router.include_router(planner_router)
v1_router.include_router(queue_router)
