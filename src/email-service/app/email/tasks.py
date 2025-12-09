import logging
from datetime import datetime

from app.settings import settings

from .manager import create_message, mail

logger = logging.getLogger(__name__)


async def user_verify_mail_event(recipient: str, link: str, username: str):
    logger.info("Sending verification email to %s", recipient)
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
    logger.info("Verification email sent to %s", recipient)


async def user_password_reset_mail(recipient: str, link: str, username: str):
    logger.info("Sending password reset email to %s", recipient)
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
    logger.info("Password reset email sent to %s", recipient)
