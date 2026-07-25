"""FastAPI main application entrypoint with middleware, OpenAPI metadata, and exception handling."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.api.v1.middleware.logging import RequestLoggingMiddleware
from app.api.v1.middleware.exception_handlers import register_exception_handlers

app = FastAPI(
    title="FinShield AI Enterprise Intelligence Platform",
    description="Enterprise Anti-Money Laundering (AML) risk evaluation, anomaly detection, and explainability REST API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Setup CORS for React Dashboard and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# Register Exception Handlers
register_exception_handlers(app)

# Include Central API Router (prefixing /api)
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["System Operations"])
def health_check():
    """Root health check endpoint."""
    return {"status": "ok", "service": "FinShield AI Backend", "version": "1.0.0"}
