"""
Middleware components for request/response logging and monitoring.

This module provides middleware for:
- Request/Response logging with correlation IDs
- Performance monitoring (request duration)
- Error tracking
- Security headers
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import correlation_id_var

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all HTTP requests and responses.

    Features:
    - Generates unique correlation ID for each request
    - Logs request details (method, path, headers, client IP)
    - Logs response details (status code, duration)
    - Adds correlation ID to response headers for client-side tracking
    - Excludes health check endpoints to reduce noise
    """

    # Endpoints to exclude from detailed logging (reduce noise)
    EXCLUDED_PATHS = {"/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID for request tracking
        correlation_id = str(uuid.uuid4())

        # Add correlation ID to request state for use in route handlers
        request.state.correlation_id = correlation_id

        # Set correlation ID in contextvars for automatic propagation to all logs
        correlation_id_var.set(correlation_id)

        # Skip detailed logging for excluded paths
        skip_logging = request.url.path in self.EXCLUDED_PATHS

        # Start timing
        start_time = time.time()

        # Log incoming request
        if not skip_logging:
            self._log_request(request, correlation_id)

        # Process request and handle errors
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception with correlation ID
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                exc_info=exc,
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "ip_address": self._get_client_ip(request),
                },
            )
            raise

        # Calculate request duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        if not skip_logging:
            self._log_response(request, response, correlation_id, duration_ms)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-Duration-Ms"] = str(round(duration_ms, 2))

        return response

    def _log_request(self, request: Request, correlation_id: str) -> None:
        """Log incoming request details."""
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "endpoint": request.url.path,
                "query_params": dict(request.query_params),
                "ip_address": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "unknown"),
                "content_type": request.headers.get("content-type"),
            },
        )

    def _log_response(
        self,
        request: Request,
        response: Response,
        correlation_id: str,
        duration_ms: float,
    ) -> None:
        """Log response details."""
        log_level = self._get_log_level_for_status(response.status_code)

        logger.log(
            log_level,
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
                "ip_address": self._get_client_ip(request),
            },
        )

        # Log slow requests (> 1 second)
        if duration_ms > 1000:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "status_code": response.status_code,
                },
            )

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """
        Extract client IP address from request.

        Handles proxy headers (X-Forwarded-For, X-Real-IP) for proper
        IP detection behind reverse proxies (nginx, load balancers).
        """
        # Check for proxy headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        if request.client:
            return request.client.host

        return "unknown"

    @staticmethod
    def _get_log_level_for_status(status_code: int) -> int:
        """Determine appropriate log level based on HTTP status code."""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        else:
            return logging.INFO

