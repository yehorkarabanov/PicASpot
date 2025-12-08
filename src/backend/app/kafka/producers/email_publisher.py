"""
Email event publisher.

Handles publishing of email-related events to Kafka.
"""

import logging
from typing import Any

from pydantic import EmailStr

from ..config import KafkaTopics
from ..schemas.email_events import EmailEventPayload, EmailEventType
from .base import BasePublisher

logger = logging.getLogger(__name__)


class EmailPublisher(BasePublisher):
    """
    Publisher for email-related events.

    Provides type-safe methods for publishing different types
    of email events to Kafka.
    """

    def __init__(self):
        """Initialize the email publisher."""
        super().__init__(topic=KafkaTopics.EMAIL_EVENTS)

    async def publish_verification_email(
        self,
        email: EmailStr,
        username: str,
        verification_link: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish an email verification event.

        Args:
            email: Recipient's email address
            username: User's username
            verification_link: URL for email verification
            metadata: Optional additional metadata

        Raises:
            Exception: If event publishing fails
        """
        try:
            event = EmailEventPayload(
                email_type=EmailEventType.VERIFICATION,
                recipient=email,
                username=username,
                link=verification_link,
                metadata=metadata or {},
            )

            await self.publish(
                event=event.model_dump(mode="json"),
                key=str(email),  # Use email as partition key for ordered processing
            )

            logger.info(
                "Published email verification event for user: %s (email: %s)",
                username,
                email,
            )

        except Exception as e:
            logger.error(
                "Failed to publish email verification event for %s: %s",
                email,
                str(e),
                exc_info=True,
            )
            raise

    async def publish_password_reset_email(
        self,
        email: EmailStr,
        username: str,
        reset_link: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish a password reset event.

        Args:
            email: Recipient's email address
            username: User's username
            reset_link: URL for password reset
            metadata: Optional additional metadata

        Raises:
            Exception: If event publishing fails
        """
        try:
            event = EmailEventPayload(
                email_type=EmailEventType.PASSWORD_RESET,
                recipient=email,
                username=username,
                link=reset_link,
                metadata=metadata or {},
            )

            await self.publish(
                event=event.model_dump(mode="json"),
                key=str(email),  # Use email as partition key for ordered processing
            )

            logger.info(
                "Published password reset event for user: %s (email: %s)",
                username,
                email,
            )

        except Exception as e:
            logger.error(
                "Failed to publish password reset event for %s: %s",
                email,
                str(e),
                exc_info=True,
            )
            raise

    async def publish_welcome_email(
        self,
        email: EmailStr,
        username: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Publish a welcome email event.

        Args:
            email: Recipient's email address
            username: User's username
            metadata: Optional additional metadata

        Raises:
            Exception: If event publishing fails
        """
        try:
            event = EmailEventPayload(
                email_type=EmailEventType.WELCOME,
                recipient=email,
                username=username,
                link="",  # No link needed for welcome email
                metadata=metadata or {},
            )

            await self.publish(
                event=event.model_dump(mode="json"),
                key=str(email),
            )

            logger.info(
                "Published welcome email event for user: %s (email: %s)",
                username,
                email,
            )

        except Exception as e:
            logger.error(
                "Failed to publish welcome email event for %s: %s",
                email,
                str(e),
                exc_info=True,
            )
            raise

