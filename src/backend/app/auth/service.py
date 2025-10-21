from pydantic import EmailStr

from app.auth.repository import UserRepository
from app.auth.schemas import UserCreate
from app.auth.security import TokenType, create_verification_token, get_password_hash
from app.celery.tasks.email_tasks.tasks import user_verify_mail_event
from app.core.exceptions import BadRequestError
from app.settings import settings


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, user_data: UserCreate) -> None:
        exising_user = await self.user_repository.get_by_field("email", user_data.email)
        if exising_user:
            raise BadRequestError(
                "User with email {email} already exists".format(email=user_data.email)
            )

        hashed_password = get_password_hash(user_data.password)
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
        }
        user = await self.user_repository.create(user_dict)

        verification_token = await create_verification_token(
            user_id=str(user.id), token_type=TokenType.VERIFICATION, use_redis=False
        )
        link = f"{settings.VERIFY_EMAIL_URL}/{verification_token}"
        user_verify_mail_event.delay(user_data.email, link, user.username)

    async def resend_verification_email(self, email: EmailStr) -> None:
        user = await self.user_repository.get_by_field("email", email)
        if not user:
            raise BadRequestError("User with this email does not exist")

        if user.is_verified:
            raise BadRequestError("User is already verified")

        verification_token = await create_verification_token(
            user_id=str(user.id), token_type=TokenType.VERIFICATION, use_redis=False
        )
        link = f"{settings.VERIFY_EMAIL_URL}/{verification_token}"
        user_verify_mail_event.delay(email, link, user.username)


