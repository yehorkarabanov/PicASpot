"""Email event schemas."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr


class EmailType(str, Enum):
    """Email types supported by the service."""

    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"


class EmailEvent(BaseModel):
    """Email event data structure from Kafka."""

    email_type: EmailType
    recipient: EmailStr
    username: str
    link: str
    timestamp: datetime | None = None
    metadata: dict[str, Any] | None = None

    class Config:
        """Pydantic config."""

        use_enum_values = True
