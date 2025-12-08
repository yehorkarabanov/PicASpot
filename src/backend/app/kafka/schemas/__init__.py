"""
Kafka event schemas.

Defines Pydantic models for all Kafka events to ensure
type safety and validation.
"""

from .email_events import EmailEventPayload, EmailEventType

__all__ = [
    "EmailEventPayload",
    "EmailEventType",
]

