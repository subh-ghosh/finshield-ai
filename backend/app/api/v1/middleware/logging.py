"""FastAPI request logging middleware measuring latency and logging endpoint access."""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.utils.logger import get_logger

logger = get_logger("api.middleware.logging")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware recording process duration and status code without logging sensitive headers or payload contents."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()
        
        # Process request
        response = await call_next(request)
        
        process_time_ms = (time.perf_counter() - start_time) * 1000.0
        
        # Add latency header
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        
        logger.info(
            f"HTTP {request.method} {request.url.path} - Status: {response.status_code} - Latency: {process_time_ms:.2f}ms"
        )
        return response
