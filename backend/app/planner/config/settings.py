"""Planner settings loaded from environment variables via Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class PlannerSettings(BaseSettings):
    """All planner configuration sourced from environment variables with safe defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # REST API
    FINSHIELD_API_BASE_URL: str = "http://localhost:8000"

    # LLM
    PLANNER_LLM_MODEL: str = "gemini-1.5-pro"
    PLANNER_LLM_TEMPERATURE: float = 0.0

    # HTTP Client
    PLANNER_REQUEST_TIMEOUT: float = 30.0
    PLANNER_RETRY_COUNT: int = 3

    # Planner Behaviour
    PLANNER_MAX_ITERATIONS: int = 3
    PLANNER_LOG_LEVEL: str = "INFO"
    PLANNER_USE_ENTERPRISE: bool = True
    PLANNER_PROPAGATE_CORRELATION_ID: bool = True
