"""
Centralized logging configuration for the Email Service.

This module provides a production-ready logging setup with:
- Structured JSON logging for production
- Human-readable console logging for development
- Log rotation to prevent disk space issues
- Integration with Kafka and FastAPI-Mail
- Different log levels per environment
- Async-safe file logging using QueueHandler
"""

import logging
import sys
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue
from typing import Any

from ..settings import settings


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
            "service": settings.SERVICE_NAME,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra context fields
        if hasattr(record, "recipient"):
            log_data["recipient"] = record.recipient
        if hasattr(record, "email_type"):
            log_data["email_type"] = record.email_type
        if hasattr(record, "kafka_offset"):
            log_data["kafka_offset"] = record.kafka_offset
        if hasattr(record, "kafka_partition"):
            log_data["kafka_partition"] = record.kafka_partition

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
        "smtp_password",
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


# Global queue listener for async-safe logging
_queue_listener: QueueListener | None = None


def setup_logging(use_file_logging: bool = True) -> None:
    """
    Configure logging for the email service.

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

    # Add file logging if enabled
    if use_file_logging:
        # Create logs directory in project root (shared with backend)
        log_dir = settings.BASE_DIR.parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # Service-specific file names
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
    # Kafka
    logging.getLogger("aiokafka").setLevel("WARNING")
    logging.getLogger("kafka").setLevel("WARNING")

    # FastAPI-Mail
    logging.getLogger("fastapi_mail").setLevel("INFO")

    # Asyncio
    logging.getLogger("asyncio").setLevel("WARNING")


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
