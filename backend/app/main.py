"""FastAPI main application entrypoint with middleware, OpenAPI metadata, and exception handling."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.v1.middleware.logging import RequestLoggingMiddleware
from app.api.v1.middleware.exception_handlers import register_exception_handlers
import logging
import asyncio

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the pipeline cache at startup so all first user requests are instant."""
    logger.info("FinShield AI: Pre-warming pipeline cache on startup...")
    try:
        # Run blocking pipeline load in a thread pool to not block the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _prewarm_pipeline)
        logger.info("FinShield AI: Pipeline cache warm - server ready for requests.")
    except Exception as e:
        logger.warning(f"Pipeline pre-warm failed (will load on first request): {e}")
    yield  # Server is running
    logger.info("FinShield AI: Shutting down.")


def _prewarm_pipeline():
    """Load and cache the full pipeline synchronously."""
    from app.api.v1.dependencies import get_pipeline_result
    try:
        get_pipeline_result()
    except Exception as e:
        logger.warning(f"Pre-warm exception: {e}")


app = FastAPI(
    title="FinShield AI Enterprise Intelligence Platform",
    description="Enterprise Anti-Money Laundering (AML) risk evaluation, anomaly detection, and explainability REST API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

import os
# Setup CORS for React Dashboard and external clients
allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")] if allowed_origins_str != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Register Exception Handlers
register_exception_handlers(app)

from fastapi import Depends
from app.api.v1.middleware.auth import verify_api_key

# Include Central API Router (prefixing /api)
app.include_router(api_router, prefix="/api", dependencies=[Depends(verify_api_key)])


@app.get("/health", tags=["System Operations"])
def health_check():
    """Root health check endpoint."""
    return {"status": "ok", "service": "FinShield AI Intelligence API", "version": "1.0.0"}

