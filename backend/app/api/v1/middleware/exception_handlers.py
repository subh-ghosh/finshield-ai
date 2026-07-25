"""Centralized exception handlers formatting standardized HTTP error responses."""

import time
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.schemas.responses import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger("api.middleware.exceptions")

def register_exception_handlers(app) -> None:
    """Registers global exception handlers on the FastAPI application instance.

    Args:
        app: FastAPI app instance.
    """
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTPException [{exc.status_code}] on {request.url.path}: {exc.detail}")
        
        error_code = "HTTP_ERROR"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            error_code = "RESOURCE_NOT_FOUND"
        elif exc.status_code == status.HTTP_400_BAD_REQUEST:
            error_code = "BAD_REQUEST"
        elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
            error_code = "VALIDATION_ERROR"
            
        error_body = ErrorResponse(
            error_code=error_code,
            message=str(exc.detail),
            details=None,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(error_body)
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"RequestValidationError on {request.url.path}: {exc.errors()}")
        
        error_body = ErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request body or query parameter validation failed",
            details=str(exc.errors()),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(error_body)
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled Exception on {request.url.path}: {str(exc)}")
        
        error_body = ErrorResponse(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred during processing",
            details=str(exc),
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(error_body)
        )
