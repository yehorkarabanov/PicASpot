"""
Centralized logging configuration for the PicASpot application.

This module provides a production-ready logging setup with:
- Structured JSON logging for production
- Human-readable console logging for development
- Log rotation to prevent disk space issues
- Integration with FastAPI, Uvicorn, SQLAlchemy, Celery, and Redis
- Different log levels per environment
- Request correlation IDs support
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Any

from app.settings import settings


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Outputs logs in a consistent JSON format that can be easily parsed
    by log aggregation tools (ELK, Datadog, CloudWatch, etc.).
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime

        log_data: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID if present (set by middleware)
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id

        # Add extra context fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class SensitiveDataFilter(logging.Filter):
    """
    Filter to prevent logging of sensitive information.

    Redacts common sensitive fields from log messages.
    """

    SENSITIVE_KEYS = {
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "credit_card",
        "ssn",
    }

    def filter(self, record: logging.LogRecord) -> bool:
        # Check message for sensitive data patterns
        message = record.getMessage().lower()
        for key in self.SENSITIVE_KEYS:
            if key in message:
                record.msg = record.msg.replace(
                    record.msg[record.msg.lower().find(key) :],
                    f"{key.upper()}_REDACTED",
                )
        return True


def get_log_level() -> str:
    """Get the appropriate log level based on environment."""
    if settings.DEBUG:
        return "DEBUG"
    return "INFO"


def setup_logging() -> None:
    """
    Configure logging for the entire application.

    This should be called once at application startup.
    Sets up handlers, formatters, and loggers for all components.
    """
    log_level = get_log_level()

    # Create logs directory if it doesn't exist
    log_dir = settings.ROOT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)


    # Console Handler - Human-readable in dev, JSON in prod
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    if settings.DEBUG:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    else:
        console_handler.setFormatter(JSONFormatter())

    # File Handler - Always JSON, with rotation
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_handler.setLevel("INFO")  # Always INFO or above for file logs
    file_handler.setFormatter(JSONFormatter())

    # Error File Handler - Separate file for errors
    error_file_handler = RotatingFileHandler(
        filename=log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    error_file_handler.setLevel("ERROR")
    error_file_handler.setFormatter(JSONFormatter())

    # Add sensitive data filter to all handlers
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)
    file_handler.addFilter(sensitive_filter)
    error_file_handler.addFilter(sensitive_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)

    # Configure application logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)

    # Configure third-party library loggers
    # Uvicorn - FastAPI's ASGI server
    logging.getLogger("uvicorn").setLevel("INFO")
    logging.getLogger("uvicorn.access").setLevel("INFO")
    logging.getLogger("uvicorn.error").setLevel("INFO")

    # FastAPI
    logging.getLogger("fastapi").setLevel("INFO")

    # SQLAlchemy - Control database query logging
    if settings.DEBUG:
        # Show SQL queries in debug mode
        logging.getLogger("sqlalchemy.engine").setLevel("INFO")
        logging.getLogger("sqlalchemy.pool").setLevel("DEBUG")
    else:
        # Reduce noise in production
        logging.getLogger("sqlalchemy.engine").setLevel("WARNING")
        logging.getLogger("sqlalchemy.pool").setLevel("WARNING")

    # Celery - Async task processing
    logging.getLogger("celery").setLevel("INFO")
    logging.getLogger("celery.worker").setLevel("INFO")
    logging.getLogger("celery.task").setLevel("INFO")

    # Redis
    logging.getLogger("redis").setLevel("WARNING")  # Redis can be noisy

    # Alembic - Database migrations
    logging.getLogger("alembic").setLevel("INFO")

    # HTTP clients
    logging.getLogger("httpx").setLevel("WARNING")
    logging.getLogger("httpcore").setLevel("WARNING")

    # Email
    logging.getLogger("fastapi_mail").setLevel("INFO")
