"""Typed exception hierarchy for the FinShield API client."""


class PlannerAPIError(Exception):
    """Base class for all planner API errors."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class APIUnavailableError(PlannerAPIError):
    """Raised on 5xx responses or connection failures. Eligible for retry."""


class APITimeoutError(PlannerAPIError):
    """Raised when request or connection times out. Eligible for retry."""


class APINotFoundError(PlannerAPIError):
    """Raised on HTTP 404. Not retried."""


class APIValidationError(PlannerAPIError):
    """Raised on HTTP 400 or 422 client validation errors. Not retried."""
