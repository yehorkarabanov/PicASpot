import logging
from zoneinfo import ZoneInfo

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

logger = logging.getLogger(__name__)


class AuthService:
    """
    Service layer for managing authentication operations.

    This service handles user registration, login, email verification,
    password reset, and token management.
    """

    def __init__(
        self, user_repository: UserRepository, timezone: ZoneInfo | None = None
    ):
        """
        Initialize the AuthService.

        Args:
            user_repository: Repository instance for user data access.
            timezone: Client's timezone for datetime conversion in responses.
        """
        self.user_repository = user_repository
        self.timezone = timezone or ZoneInfo("UTC")

    # TODO: add opt flow
    async def register(self, user_data: UserCreate) -> None:
        """
        Register a new user account.

        Creates a new user with hashed password. Email verification is currently
        bypassed (is_verified=True) but should be implemented with OTP flow.

        Args:
            user_data: User registration data including username, email, and password.

        Raises:
            BadRequestError: If email or username already exists.
        """
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

        logger.info("User registered successfully: %s", user.email)

        # verification_token = await create_verification_token(
        #     user_id=str(user.id), token_type=TokenType.VERIFICATION, use_redis=False
        # )
        # link = f"{settings.VERIFY_EMAIL_URL}{verification_token}"
        # user_verify_mail_event.delay(user_data.email, link, user.username)

    # TODO: redo to send otp
    async def resend_verification_token(self, email: EmailStr) -> None:
        """
        Resend email verification token to a user.

        Args:
            email: The email address of the user requesting verification token.

        Raises:
            BadRequestError: If user does not exist or is already verified.
        """
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
        """
        Authenticate a user and generate access token.

        Accepts either email or username for login. Validates password and
        ensures user's email is verified before allowing login.

        Args:
            user_data: Login credentials (username/email and password).

        Returns:
            UserLoginResponse: User information and access token.

        Raises:
            BadRequestError: If credentials are invalid or user is not verified.
        """
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
        logger.info("User logged in: %s", user.username)

        # Create login response data with timezone conversion
        login_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "token": AccessToken(access_token=access_token),
        }

        return UserLoginResponse.model_validate_with_timezone(login_data, self.timezone)

    # TODO: redo to verify otp
    async def verify_token(self, token: str) -> None:
        """
        Verify an email verification token and activate user account.

        Args:
            token: The verification token sent to user's email.

        Raises:
            AuthenticationError: If token is invalid, expired, or has wrong type.
            NotFoundError: If user associated with token does not exist.
        """
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
        logger.info("User verified: %s", user.email)

    async def send_password_reset_token(self, email: EmailStr) -> None:
        """
        Send a password reset token to user's email.

        Generates a time-limited token and sends it via email for password reset.

        Args:
            email: The email address of the user requesting password reset.

        Raises:
            BadRequestError: If user with this email does not exist.
        """
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
        logger.info("Password reset email sent to %s", email)

    async def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset user's password using a valid reset token.

        Validates the reset token, updates the user's password, and invalidates
        the token to prevent reuse.

        Args:
            token: The password reset token sent to user's email.
            new_password: The new password to set for the user.

        Raises:
            AuthenticationError: If token is invalid, expired, or has wrong type.
            NotFoundError: If user associated with token does not exist.
        """
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
        logger.info("Password reset for user: %s", user.email)
