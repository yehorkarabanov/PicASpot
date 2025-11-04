"""
Custom exception handlers for the FastAPI application.
Provides consistent error response formats across the API.
"""

import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.schemas import (
    ValidationErrorData,
    ValidationErrorDetail,
    ValidationErrorReturn,
)
from app.settings import settings

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors.
    Transforms the default error format to match our BaseReturn schema.
    """
    errors = []
    for error in exc.errors():
        # Extract field name from location tuple (e.g., ('body', 'password') -> 'password')
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")

        # Extract user-friendly message
        msg = error.get("msg", "")
        # For custom field_validator errors with ValueError, extract the actual message
        if error["type"] == "value_error" and "ctx" in error:
            ctx_error = error["ctx"].get("error")
            if ctx_error and hasattr(ctx_error, "args") and ctx_error.args:
                msg = str(ctx_error.args[0])
            elif isinstance(ctx_error, str):
                msg = ctx_error

        errors.append(
            ValidationErrorDetail(
                field=field_path, message=msg, type=error["type"]
            ).model_dump()
        )

    logger.warning(
        "Validation error",
        extra={"path": request.url.path, "method": request.method, "errors": errors},
    )

    # Use ValidationErrorReturn schema which fits BaseReturn structure
    error_details = [ValidationErrorDetail(**error) for error in errors]
    response = ValidationErrorReturn(
        message="Validation failed", data=ValidationErrorData(errors=error_details)
    )

    return JSONResponse(status_code=422, content=response.model_dump())


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    Logs the error and returns a generic error response in production.
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={"path": request.url.path, "method": request.method},
    )
    if settings.DEBUG:
        raise exc
    return JSONResponse(status_code=500, content={"message": "Internal server error"})
