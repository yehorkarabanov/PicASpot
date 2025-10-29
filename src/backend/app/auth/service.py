from pydantic import EmailStr

from app.celery.tasks.email_tasks.tasks import (
    user_password_reset_mail,
    user_verify_mail_event,
)
from app.core.exceptions import AuthenticationError, BadRequestError, NotFoundError
from app.settings import settings
from app.user.repository import UserRepository

from .schemas import AccessToken, UserCreate, UserLogin, UserLoginResponse
from .security import (
    TokenType,
    create_access_token,
    create_verification_token,
    decode_verification_token,
    delete_verification_token,
    get_password_hash,
    verify_password,
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    # TODO: add opt flow
    async def register(self, user_data: UserCreate) -> None:
        existing_user = await self.user_repository.get_by_email_or_username(
            user_data.email, user_data.username
        )
        if existing_user:
            if existing_user.email == user_data.email:
                raise BadRequestError("User with this email already exists")
            else:
                raise BadRequestError("User with this username already exists")

        hashed_password = get_password_hash(user_data.password)
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_verified": True,  # TODO: Set to False when OTP will be done
        }
        user = await self.user_repository.create(user_dict)  # noqa: F841

        # verification_token = await create_verification_token(
        #     user_id=str(user.id), token_type=TokenType.VERIFICATION, use_redis=False
        # )
        # link = f"{settings.VERIFY_EMAIL_URL}{verification_token}"
        # user_verify_mail_event.delay(user_data.email, link, user.username)

    # TODO: redo to send otp
    async def resend_verification_token(self, email: EmailStr) -> None:
        user = await self.user_repository.get_by_field("email", email)
        if not user:
            raise BadRequestError("User with this email does not exist")

        if user.is_verified:
            raise BadRequestError("User is already verified")

        verification_token = await create_verification_token(
            user_id=str(user.id), token_type=TokenType.VERIFICATION, use_redis=True
        )
        link = f"{settings.VERIFY_EMAIL_URL}{verification_token}"
        user_verify_mail_event.delay(email, link, user.username)

    async def login(self, user_data: UserLogin) -> UserLoginResponse:
        if "@" in user_data.username:
            user = await self.user_repository.get_by_field("email", user_data.username)
        else:
            user = await self.user_repository.get_by_field(
                "username", user_data.username
            )
        if not user:
            raise BadRequestError("Invalid email or password")

        if not verify_password(user_data.password, user.hashed_password):
            raise BadRequestError("Invalid email or password")

        if not user.is_verified:
            raise BadRequestError("Please verify your email before logging in")

        access_token = create_access_token(subject=str(user.id))
        return UserLoginResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_superuser=user.is_superuser,
            is_verified=user.is_verified,
            token=AccessToken(access_token=access_token),
        )

    # TODO: redo to verify otp
    async def verify_token(self, token: str) -> None:
        token_data = await decode_verification_token(token, use_redis=True)
        if not token_data:
            raise AuthenticationError("Invalid or expired verification token")

        user_id = token_data.get("user_id")
        token_type = token_data.get("type")

        if token_type != TokenType.VERIFICATION.value:
            raise AuthenticationError("Invalid token type")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if user.is_verified:
            raise AuthenticationError("User is already verified")

        # Mark user as verified
        user.is_verified = True
        await self.user_repository.save(user)

    async def send_password_reset_token(self, email: EmailStr) -> None:
        user = await self.user_repository.get_by_field("email", email)
        if not user:
            raise BadRequestError("User with this email does not exist")

        reset_token = await create_verification_token(
            user_id=str(user.id), token_type=TokenType.PASSWORD_RESET
        )
        link = f"{settings.EMAIL_RESET_PASSWORD_URL}/{reset_token}"
        user_password_reset_mail.delay(
            user.email,
            link,
            user.username,
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        token_data = await decode_verification_token(token)
        if not token_data:
            raise AuthenticationError("Invalid or expired password reset token")

        user_id = token_data.get("user_id")
        token_type = token_data.get("type")

        if token_type != TokenType.PASSWORD_RESET.value:
            raise AuthenticationError("Invalid token type")

        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        # Update user's password
        user.hashed_password = get_password_hash(new_password)
        await self.user_repository.save(user)

        await delete_verification_token(token)
