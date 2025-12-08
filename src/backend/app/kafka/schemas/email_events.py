"""
Email event schemas for Kafka messages.

Defines the structure of email-related events published to Kafka.
These schemas must match the consumer expectations in the email-service.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmailEventType(str, Enum):
    """Types of email events that can be published."""

    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    WELCOME = "welcome"
    NOTIFICATION = "notification"


class EmailEventPayload(BaseModel):
    """
    Schema for email events published to Kafka.

    This schema matches the consumer's expectations in the email-service.

    Attributes:
        email_type: Type of email to send
        recipient: Email address of the recipient
        username: Username of the recipient
        link: Action link for the email (verification, reset, etc.)
        timestamp: Event creation timestamp (auto-generated)
        metadata: Additional metadata for the email
    """

    email_type: EmailEventType
    recipient: EmailStr
    username: str
    link: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

