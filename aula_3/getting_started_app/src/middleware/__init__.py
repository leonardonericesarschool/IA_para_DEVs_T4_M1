"""FastAPI middleware for exception handling"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.exceptions import PixKeysException
from src.logging_config import get_logger
import traceback
from uuid import uuid4

logger = get_logger(__name__)


async def exception_handler(request: Request, exc: PixKeysException) -> JSONResponse:
    """Handle PixKeys domain/application exceptions"""
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details if exc.details else None
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    
    # Extract field errors
    field_errors = {}
    for error in exc.errors():
        field_name = '.'.join(str(x) for x in error['loc'][1:])
        field_errors[field_name] = error['msg']
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {
                    "fields": field_errors
                }
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
        }
    )


async def logging_middleware(request: Request, call_next):
    """Middleware for request logging with request_id"""
    
    # Generate or extract request_id
    request_id = request.headers.get('X-Request-ID', str(uuid4()))
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        f"{request.method} {request.url.path}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Add request_id to response headers
    response.headers["X-Request-ID"] = request_id
    
    # Log response
    logger.info(
        f"{request.method} {request.url.path} {response.status_code}",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code
        }
    )
    
    return response


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with FastAPI app"""
    app.add_exception_handler(PixKeysException, exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
