from datetime import datetime

from asgiref.sync import async_to_sync

from app.celery.worker import celery
from app.settings import settings

from .manager import create_message, mail


@celery.task
def user_verify_mail_event(recipient: str, link: str, username: str):
    message = create_message(
        recipients=[
            recipient,
        ],
        subject=f"{settings.PROJECT_NAME} | Verify Your Email",
        body={
            "verification_link": link,
            "username": username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.now().year,
        },
    )
    async_to_sync(mail.send_message)(message, "verify.html")


@celery.task
def user_password_reset_mail(recipient: str, link: str, username: str):
    message = create_message(
        recipients=[
            recipient,
        ],
        subject=f"{settings.PROJECT_NAME} | Reset Your Password",
        body={
            "reset_link": link,
            "username": username,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "year": datetime.now().year,
        },
    )
    async_to_sync(mail.send_message)(message, "password_reset.html")
