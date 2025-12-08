"""Email event schemas and data models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr


class EmailType(str, Enum):
    """Enumeration of supported email types."""

    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


class EmailEvent(BaseModel):
    """Pydantic model for email event data from Kafka.

    Attributes:
        email_type: The type of email to send
        recipient: Email address of the recipient
        username: Username of the recipient
        link: Link to include in the email (verification or reset)
        timestamp: Optional timestamp of the event
        metadata: Optional additional metadata
    """

    email_type: EmailType
    recipient: EmailStr
    username: str
    link: str
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
