"""
Centralized logging configuration for the Image Service.

This module provides a production-ready logging setup with:
- Structured JSON logging for production
- Human-readable console logging for development
- Log rotation to prevent disk space issues
- Integration with FastAPI and Kafka
- Different log levels per environment
- Service-specific context support
"""

import logging
import sys
from contextvars import ContextVar
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue
from typing import Any

from app.settings import settings

# Context variable for correlation ID propagation
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)


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
            "service": settings.SERVICE_NAME,  # Identify which container/service
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation ID from context or record
        correlation_id = (
            getattr(record, "correlation_id", None) or correlation_id_var.get()
        )
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add extra context fields - image service specific
        if hasattr(record, "image_id"):
            log_data["image_id"] = record.image_id
        if hasattr(record, "kafka_topic"):
            log_data["kafka_topic"] = record.kafka_topic
        if hasattr(record, "kafka_partition"):
            log_data["kafka_partition"] = record.kafka_partition
        if hasattr(record, "kafka_offset"):
            log_data["kafka_offset"] = record.kafka_offset

        # Add generic extra context fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "username"):
            log_data["username"] = record.username
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

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
        # Get the formatted message
        message = record.getMessage()

        # Redact sensitive information
        redacted_message = message
        for key in self.SENSITIVE_KEYS:
            if key in redacted_message.lower():
                redacted_message = redacted_message.replace(
                    key, f"{key.upper()}_REDACTED"
                )

        # If redaction occurred, update the record to use the redacted message directly
        if redacted_message != message:
            record.msg = redacted_message
            record.args = ()

        return True


def get_log_level() -> str:
    """Get the appropriate log level based on environment."""
    if settings.DEBUG:
        return "DEBUG"
    return "INFO"


# Global queue listener for async-safe logging
_queue_listener: QueueListener | None = None


def setup_logging(use_file_logging: bool = True) -> None:
    """
    Configure logging for the entire application.

    This should be called once at application startup.
    Sets up handlers, formatters, and loggers for all components.
    Uses QueueHandler/QueueListener for async-safe file I/O.

    Args:
        use_file_logging: If False, only logs to stdout (Docker best practice).
                         If True, logs to both stdout and service-specific files.
    """
    global _queue_listener

    log_level = get_log_level()
    service_name = settings.SERVICE_NAME

    # Console Handler - Human-readable in dev, JSON in prod
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    if settings.DEBUG:
        console_handler.setFormatter(
            logging.Formatter(
                f"[{service_name}] %(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    else:
        console_handler.setFormatter(JSONFormatter())

    # Add sensitive data filter to console
    sensitive_filter = SensitiveDataFilter()
    console_handler.addFilter(sensitive_filter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(console_handler)

    # Add file logging if enabled (separate files per service to avoid conflicts)
    if use_file_logging:
        # Create logs directory if it doesn't exist
        log_dir = settings.ROOT_DIR / "logs"
        log_dir.mkdir(exist_ok=True)

        # Service-specific file names to prevent Docker container conflicts
        # image-service container → logs/image-service.log
        service_log_file = log_dir / f"{service_name}.log"
        service_error_file = log_dir / f"{service_name}-error.log"

        # File Handler - Always JSON, with rotation
        file_handler = RotatingFileHandler(
            filename=service_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,  # Keep 5 backup files
            encoding="utf-8",
        )
        file_handler.setLevel("INFO")  # Always INFO or above for file logs
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(sensitive_filter)

        # Error File Handler - Separate file for errors
        error_file_handler = RotatingFileHandler(
            filename=service_error_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        error_file_handler.setLevel("ERROR")
        error_file_handler.setFormatter(JSONFormatter())
        error_file_handler.addFilter(sensitive_filter)

        # Create queue for async-safe file logging
        log_queue: Queue = Queue(-1)  # Unlimited queue size
        queue_handler = QueueHandler(log_queue)

        # Start queue listener in a separate thread for file handlers
        # This prevents blocking the async event loop
        _queue_listener = QueueListener(
            log_queue, file_handler, error_file_handler, respect_handler_level=True
        )
        _queue_listener.start()

        root_logger.addHandler(queue_handler)  # Use queue for file logging

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

    # Kafka
    logging.getLogger("aiokafka").setLevel("WARNING")
    logging.getLogger("aiokafka.conn").setLevel("WARNING")
    logging.getLogger("aiokafka.cluster").setLevel("WARNING")
    logging.getLogger("aiokafka.consumer").setLevel("WARNING")
    logging.getLogger("aiokafka.producer").setLevel("WARNING")

    # HTTP clients
    logging.getLogger("httpx").setLevel("WARNING")
    logging.getLogger("httpcore").setLevel("WARNING")

    # Watchfiles - File watching for hot reload
    logging.getLogger("watchfiles").setLevel("WARNING")
    logging.getLogger("watchfiles.main").setLevel("WARNING")


def shutdown_logging() -> None:
    """
    Shutdown logging gracefully.

    Should be called during application shutdown to:
    - Stop the queue listener
    - Flush any pending log messages
    - Close file handlers properly
    """
    global _queue_listener
    if _queue_listener:
        _queue_listener.stop()
        _queue_listener = None
