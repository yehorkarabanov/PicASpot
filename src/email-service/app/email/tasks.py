import logging
from datetime import datetime

from app.settings import settings

from .manager import create_message, mail

logger = logging.getLogger(__name__)


async def user_verify_mail(recipient: str, link: str, username: str):
    """Send verification email to user."""
    logger.info(
        "Sending verification email",
        extra={
            "email_to": recipient,
            "username": username,
            "email_template": "verify.html",
            "email_subject": f"{settings.PROJECT_NAME} | Verify Your Email",
        },
    )
    try:
        message = create_message(
            recipients=[
                recipient,
            ],
            subject=f"{settings.PROJECT_NAME} | Verify Your Email",
            body={
                "verification_link": link,
                "username": username,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "year": str(datetime.now().year),
            },
        )
        await mail.send_message(message, "verify.html")
        logger.info(
            "Verification email sent successfully",
            extra={
                "email_to": recipient,
                "username": username,
            },
        )
    except Exception as e:
        logger.error(
            "Failed to send verification email",
            exc_info=True,
            extra={
                "email_to": recipient,
                "username": username,
                "error": str(e),
            },
        )
        raise


async def user_password_reset_mail(recipient: str, link: str, username: str):
    """Send password reset email to user."""
    logger.info(
        "Sending password reset email",
        extra={
            "email_to": recipient,
            "username": username,
            "email_template": "password_reset.html",
            "email_subject": f"{settings.PROJECT_NAME} | Reset Your Password",
        },
    )
    try:
        message = create_message(
            recipients=[
                recipient,
            ],
            subject=f"{settings.PROJECT_NAME} | Reset Your Password",
            body={
                "reset_link": link,
                "username": username,
                "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "year": str(datetime.now().year),
            },
        )
        await mail.send_message(message, "password_reset.html")
        logger.info(
            "Password reset email sent successfully",
            extra={
                "email_to": recipient,
                "username": username,
            },
        )
    except Exception as e:
        logger.error(
            "Failed to send password reset email",
            exc_info=True,
            extra={
                "email_to": recipient,
                "username": username,
                "error": str(e),
            },
        )
        raise
