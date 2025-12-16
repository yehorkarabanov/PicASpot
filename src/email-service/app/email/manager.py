import logging
from typing import Any, Dict, List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import SecretStr  # noqa: F401

from app.settings import settings

logger = logging.getLogger(__name__)

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
    TEMPLATE_FOLDER=settings.BASE_DIR / "email/templates",
)

mail = FastMail(mail_config)


def create_message(
    recipients: List[str], subject: str, body: Dict[str, Any] | None = None
) -> MessageSchema:
    """Create an email message schema for sending."""
    if body is None:
        body = {}

    logger.debug(
        "Creating email message",
        extra={
            "recipients": recipients,
            "subject": subject,
            "body_keys": list(body.keys()) if body else [],
        },
    )

    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        template_body=body,
        subtype=MessageType.html,
    )
    return message
