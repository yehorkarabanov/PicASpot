"""Email manager for sending emails using fastapi-mail."""

import asyncio
import logging
from datetime import datetime
from typing import Any

from app.core.settings import settings
from app.models.schemas import EmailEvent, EmailType
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

logger = logging.getLogger(__name__)


# Metrics for monitoring
class EmailMetrics:
    """Simple metrics tracker for email operations."""

    def __init__(self):
        self.emails_sent = 0
        self.emails_failed = 0
        self.emails_retried = 0

    def increment_sent(self):
        self.emails_sent += 1

    def increment_failed(self):
        self.emails_failed += 1

    def increment_retried(self):
        self.emails_retried += 1

    def get_stats(self) -> dict[str, int]:
        return {
            "emails_sent": self.emails_sent,
            "emails_failed": self.emails_failed,
            "emails_retried": self.emails_retried,
        }


metrics = EmailMetrics()

# Configure mail connection
ConnectionConfig.model_rebuild()
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
)

mail = FastMail(mail_config)


class EmailManager:
    """Manages email sending operations."""

    @staticmethod
    def _create_message(
        recipient: str, subject: str, body: dict[str, Any]
    ) -> MessageSchema:
        """
        Create an email message.

        Args:
            recipient: Email recipient address
            subject: Email subject line
            body: Template variables for the email

        Returns:
            MessageSchema: Configured email message
        """
        return MessageSchema(
            recipients=[recipient],
            subject=subject,
            template_body=body,
            subtype=MessageType.html,
        )

    async def _send_with_retry(
        self, message: MessageSchema, template_name: str, recipient: str
    ) -> None:
        """
        Send email with retry logic.

        Args:
            message: Email message to send
            template_name: Template file name
            recipient: Recipient email for logging
        """
        last_exception = None

        for attempt in range(settings.EMAIL_MAX_RETRIES):
            try:
                await mail.send_message(message, template_name=template_name)
                metrics.increment_sent()
                logger.info(
                    "Email sent successfully to %s (attempt %d/%d)",
                    recipient,
                    attempt + 1,
                    settings.EMAIL_MAX_RETRIES,
                )
                return
            except Exception as e:
                last_exception = e
                metrics.increment_retried()
                logger.warning(
                    "Failed to send email to %s (attempt %d/%d): %s",
                    recipient,
                    attempt + 1,
                    settings.EMAIL_MAX_RETRIES,
                    str(e),
                )

                if attempt < settings.EMAIL_MAX_RETRIES - 1:
                    await asyncio.sleep(settings.EMAIL_RETRY_DELAY_SECONDS)

        # All retries failed
        metrics.increment_failed()
        logger.error(
            "All retry attempts failed for %s: %s",
            recipient,
            str(last_exception),
            exc_info=True,
        )
        raise last_exception

    async def send_verification_email(self, event: EmailEvent) -> None:
        """
        Send a verification email.

        Args:
            event: Email event containing verification details
        """
        logger.info("Sending verification email to %s", event.recipient)

        body = {
            "verification_link": event.link,
            "username": event.username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": str(datetime.now().year),
        }

        message = self._create_message(
            recipient=str(event.recipient),
            subject=f"{settings.PROJECT_NAME} | Verify Your Email",
            body=body,
        )

        await self._send_with_retry(message, "verify.html", str(event.recipient))

    async def send_password_reset_email(self, event: EmailEvent) -> None:
        """
        Send a password reset email.

        Args:
            event: Email event containing password reset details
        """
        logger.info("Sending password reset email to %s", event.recipient)

        body = {
            "reset_link": event.link,
            "username": event.username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": str(datetime.now().year),
        }

        message = self._create_message(
            recipient=str(event.recipient),
            subject=f"{settings.PROJECT_NAME} | Reset Your Password",
            body=body,
        )

        await self._send_with_retry(message, "password_reset.html", str(event.recipient))

    async def process_email_event(self, event: EmailEvent) -> None:
        """
        Process an email event based on its type.

        Args:
            event: Email event to process
        """
        handlers = {
            EmailType.VERIFICATION: self.send_verification_email,
            EmailType.PASSWORD_RESET: self.send_password_reset_email,
        }

        handler = handlers.get(event.email_type)
        if handler:
            await handler(event)
        else:
            logger.error("Unknown email type: %s", event.email_type)
