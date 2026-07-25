"""Config package namespace."""

from app.planner.config.settings import PlannerSettings
from app.planner.config.config import get_settings

__all__ = ["PlannerSettings", "get_settings"]
