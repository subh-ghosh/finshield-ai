"""Runtime configuration singleton accessor for the planner package."""

from functools import lru_cache
from app.planner.config.settings import PlannerSettings


@lru_cache(maxsize=1)
def get_settings() -> PlannerSettings:
    """Returns lazily initialized, cached PlannerSettings singleton.

    Returns:
        PlannerSettings: Configuration loaded from environment.
    """
    return PlannerSettings()
