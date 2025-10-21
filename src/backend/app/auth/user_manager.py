import uuid
from urllib.request import Request

from fastapi_users import BaseUserManager, UUIDIDMixin

from app.auth.dependencies import UserRepositoryDep
from app.auth.models import User
from app.celery.tasks.email_tasks.tasks import (
    user_password_reset_mail,
    user_verify_mail_event,
)
from app.settings import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_forgot_password(
        self, user: User, token: str, _request: Request | None = None
    ):
        """Send password reset email via Celery task"""
        reset_link = f"{settings.DOMAIN}/auth/reset-password?token={token}"
        user_password_reset_mail.delay(
            recipient=user.email,
            link=reset_link,
            username=user.email.split("@")[0],
        )

    async def on_after_request_verify(
        self, user: User, token: str, _request: Request | None = None
    ):
        """Send email verification via Celery task"""
        verification_link = f"{settings.DOMAIN}/auth/verify?token={token}"
        user_verify_mail_event.delay(
            recipient=user.email,
            link=verification_link,
            username=user.email.split("@")[0],
        )


async def get_user_manager(user_repository: UserRepositoryDep):
    yield UserManager(user_repository)
