"""
Unit tests for AuthService.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import EmailStr

from app.auth.schemas import UserCreate, UserLogin
from app.auth.security import TokenType, create_verification_token, get_password_hash
from app.auth.service import AuthService
from app.core.exceptions import AuthenticationError, BadRequestError, NotFoundError
from app.user.models import User
from app.user.repository import UserRepository


@pytest.mark.unit
class TestAuthServiceRegistration:
    """Tests for user registration functionality."""

    @pytest.fixture
    async def auth_service(self, test_session):
        """Create AuthService instance with test repository."""
        from app.user.models import User
        user_repo = UserRepository(test_session, User)
        return AuthService(user_repository=user_repo)

    @pytest.mark.asyncio
    async def test_register_new_user_success(self, auth_service, test_session, mock_celery):
        """Test successful user registration."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

        await auth_service.register(user_data)

        # Verify user was created in database
        user = await auth_service.user_repository.get_by_field("email", user_data.email)
        assert user is not None
        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.is_verified is True  # TODO: Should be False when OTP is implemented
        assert user.hashed_password != user_data.password

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_service, test_user):
        """Test registration with existing email."""
        user_data = UserCreate(
            username="newuser",
            email=test_user.email,
            password="Password123",
        )

        with pytest.raises(BadRequestError, match="email already exists"):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, auth_service, test_user):
        """Test registration with existing username."""
        user_data = UserCreate(
            username=test_user.username,
            email="newemail@example.com",
            password="Password123",
        )

        with pytest.raises(BadRequestError, match="username already exists"):
            await auth_service.register(user_data)

    @pytest.mark.asyncio
    async def test_register_password_is_hashed(self, auth_service, test_session):
        """Test that password is properly hashed during registration."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password123",
        )

        await auth_service.register(user_data)

        user = await auth_service.user_repository.get_by_field("email", user_data.email)
        assert user.hashed_password != user_data.password
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash prefix


@pytest.mark.unit
class TestAuthServiceLogin:
    """Tests for user login functionality."""

    @pytest.fixture
    async def auth_service(self, test_session):
        """Create AuthService instance with test repository."""
        from app.user.models import User
        user_repo = UserRepository(test_session, User)
        return AuthService(user_repository=user_repo)

    @pytest.mark.asyncio
    async def test_login_with_username_success(self, auth_service, test_user):
        """Test successful login with username."""
        user_data = UserLogin(
            username=test_user.username,
            password="Password123",
        )

        response = await auth_service.login(user_data)

        assert response.username == test_user.username
        assert response.email == test_user.email
        assert response.token.access_token is not None
        assert len(response.token.access_token) > 0

    @pytest.mark.asyncio
    async def test_login_with_email_success(self, auth_service, test_user):
        """Test successful login with email."""
        user_data = UserLogin(
            username=test_user.email,  # Using email in username field
            password="Password123",
        )

        response = await auth_service.login(user_data)

        assert response.username == test_user.username
        assert response.email == test_user.email
        assert response.token.access_token is not None

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, auth_service, test_user):
        """Test login with incorrect password."""
        user_data = UserLogin(
            username=test_user.username,
            password="WrongPass123",
        )

        with pytest.raises(BadRequestError, match="Invalid email or password"):
            await auth_service.login(user_data)

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user(self, auth_service):
        """Test login with non-existent user."""
        user_data = UserLogin(
            username="nonexistent",
            password="Password123",
        )

        with pytest.raises(BadRequestError, match="Invalid email or password"):
            await auth_service.login(user_data)

    @pytest.mark.asyncio
    async def test_login_with_unverified_user(self, auth_service, unverified_user):
        """Test login with unverified user."""
        user_data = UserLogin(
            username=unverified_user.username,
            password="Password123",
        )

        with pytest.raises(BadRequestError, match="verify your email"):
            await auth_service.login(user_data)

    @pytest.mark.asyncio
    async def test_login_returns_correct_user_data(self, auth_service, test_user):
        """Test that login returns correct user data."""
        user_data = UserLogin(
            username=test_user.username,
            password="Password123",
        )

        response = await auth_service.login(user_data)

        assert response.id == test_user.id
        assert response.username == test_user.username
        assert response.email == test_user.email
        assert response.is_superuser == test_user.is_superuser
        assert response.is_verified == test_user.is_verified


@pytest.mark.unit
class TestAuthServiceVerification:
    """Tests for email verification functionality."""

    @pytest.fixture
    async def auth_service(self, test_session):
        """Create AuthService instance with test repository."""
        from app.user.models import User
        user_repo = UserRepository(test_session, User)
        return AuthService(user_repository=user_repo)

    @pytest.mark.asyncio
    async def test_verify_token_success(self, auth_service, unverified_user, mock_redis):
        """Test successful email verification."""
        # Create a verification token
        token = await create_verification_token(
            user_id=str(unverified_user.id),
            token_type=TokenType.VERIFICATION,
            use_redis=True,
        )

        # Mock Redis to return token data
        import json
        mock_redis.get.return_value = json.dumps({
            "user_id": str(unverified_user.id),
            "type": TokenType.VERIFICATION.value,
        })

        await auth_service.verify_token(token)

        # Verify user is now verified
        user = await auth_service.user_repository.get_by_id(unverified_user.id)
        assert user.is_verified is True

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self, auth_service, mock_redis):
        """Test verification with invalid token."""
        mock_redis.get.return_value = None

        with pytest.raises(AuthenticationError, match="Invalid or expired"):
            await auth_service.verify_token("invalid_token")

    @pytest.mark.asyncio
    async def test_verify_token_user_not_found(self, auth_service, mock_redis):
        """Test verification when user doesn't exist."""
        fake_user_id = str(uuid.uuid4())
        import json
        mock_redis.get.return_value = json.dumps({
            "user_id": fake_user_id,
            "type": TokenType.VERIFICATION.value,
        })

        with pytest.raises(NotFoundError, match="User not found"):
            await auth_service.verify_token("some_token")

    @pytest.mark.asyncio
    async def test_verify_token_already_verified(self, auth_service, test_user, mock_redis):
        """Test verification when user is already verified."""
        import json
        mock_redis.get.return_value = json.dumps({
            "user_id": str(test_user.id),
            "type": TokenType.VERIFICATION.value,
        })

        with pytest.raises(AuthenticationError, match="already verified"):
            await auth_service.verify_token("some_token")

    @pytest.mark.asyncio
    async def test_verify_token_wrong_type(self, auth_service, unverified_user, mock_redis):
        """Test verification with wrong token type."""
        import json
        mock_redis.get.return_value = json.dumps({
            "user_id": str(unverified_user.id),
            "type": "WRONG_TYPE",
        })

        with pytest.raises(AuthenticationError, match="Invalid token type"):
            await auth_service.verify_token("some_token")


@pytest.mark.unit
class TestAuthServicePasswordReset:
    """Tests for password reset functionality."""

    @pytest.fixture
    async def auth_service(self, test_session):
        """Create AuthService instance with test repository."""
        user_repo = UserRepository(test_session)
        return AuthService(user_repository=user_repo)

    @pytest.mark.asyncio
    async def test_resend_verification_token_success(
        self, auth_service, unverified_user, mock_celery
    ):
        """Test resending verification token to unverified user."""
        with patch("app.auth.service.create_verification_token") as mock_create_token:
            mock_create_token.return_value = "test_token"

            await auth_service.resend_verification_token(unverified_user.email)

            mock_create_token.assert_called_once()
            mock_celery["verify_email"].delay.assert_called_once()

    @pytest.mark.asyncio
    async def test_resend_verification_token_user_not_found(self, auth_service):
        """Test resending verification token for non-existent user."""
        with pytest.raises(BadRequestError, match="does not exist"):
            await auth_service.resend_verification_token("nonexistent@example.com")

    @pytest.mark.asyncio
    async def test_resend_verification_token_already_verified(
        self, auth_service, test_user
    ):
        """Test resending verification token to already verified user."""
        with pytest.raises(BadRequestError, match="already verified"):
            await auth_service.resend_verification_token(test_user.email)

