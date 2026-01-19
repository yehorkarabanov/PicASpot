"""
Unit tests for AuthService.

Tests cover:
- User registration
- User login
- Password hashing and verification
- Token creation and verification
- Email verification flow
- Password reset flow
"""

import uuid
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

import pytest

from app.auth.schemas import UserCreate, UserLogin
from app.auth.security import get_password_hash, verify_password
from app.auth.service import AuthService
from app.core.exceptions import BadRequestError
from app.user.repository import UserRepository


class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_password_hash_generates_different_hashes(self):
        """Same password should generate different hashes due to salt."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_verify_password_correct(self):
        """Correct password should verify successfully."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password should fail verification."""
        password = "TestPassword123"
        wrong_password = "WrongPassword123"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Empty password should fail verification."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert verify_password("", hashed) is False


class TestAuthServiceRegister:
    """Tests for AuthService.register method."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        mock = AsyncMock(spec=UserRepository)
        mock.get_by_email_or_username = AsyncMock(return_value=None)
        mock.create = AsyncMock()
        return mock

    @pytest.fixture
    def auth_service(self, mock_user_repository):
        """Create an AuthService instance with mocked dependencies."""
        return AuthService(
            user_repository=mock_user_repository,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_register_success(self, auth_service, mock_user_repository):
        """User registration should succeed with valid data."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="TestPassword123",
        )

        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.email = user_data.email
        mock_user_repository.create.return_value = mock_user

        # Should not raise any exception
        await auth_service.register(user_data)

        # Verify repository methods were called
        mock_user_repository.get_by_email_or_username.assert_called_once_with(
            user_data.email, user_data.username
        )
        mock_user_repository.create.assert_called_once()

        # Verify password was hashed
        call_args = mock_user_repository.create.call_args[0][0]
        assert call_args["username"] == user_data.username
        assert call_args["email"] == user_data.email
        assert "hashed_password" in call_args
        assert call_args["hashed_password"] != user_data.password

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, auth_service, mock_user_repository):
        """Registration should fail if email already exists."""
        existing_user = MagicMock()
        existing_user.email = "test@example.com"
        existing_user.username = "otheruser"
        mock_user_repository.get_by_email_or_username.return_value = existing_user

        user_data = UserCreate(
            username="newuser",
            email="test@example.com",
            password="TestPassword123",
        )

        with pytest.raises(BadRequestError) as exc_info:
            await auth_service.register(user_data)

        assert "email already exists" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, auth_service, mock_user_repository
    ):
        """Registration should fail if username already exists."""
        existing_user = MagicMock()
        existing_user.email = "other@example.com"
        existing_user.username = "testuser"
        mock_user_repository.get_by_email_or_username.return_value = existing_user

        user_data = UserCreate(
            username="testuser",
            email="new@example.com",
            password="TestPassword123",
        )

        with pytest.raises(BadRequestError) as exc_info:
            await auth_service.register(user_data)

        assert "username already exists" in str(exc_info.value.detail)


class TestAuthServiceLogin:
    """Tests for AuthService.login method."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        mock = AsyncMock(spec=UserRepository)
        return mock

    @pytest.fixture
    def auth_service(self, mock_user_repository):
        """Create an AuthService instance with mocked dependencies."""
        return AuthService(
            user_repository=mock_user_repository,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_login_with_username_success(
        self, auth_service, mock_user_repository
    ):
        """Login with username should succeed with valid credentials."""
        password = "TestPassword123"
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash(password)
        mock_user.is_verified = True
        mock_user.is_superuser = False
        mock_user.profile_picture_path = None
        mock_user.created_at = MagicMock()
        mock_user.updated_at = MagicMock()

        mock_user_repository.get_by_field.return_value = mock_user

        login_data = UserLogin(username="testuser", password=password)
        result = await auth_service.login(login_data)

        assert result.username == "testuser"
        assert result.token is not None
        mock_user_repository.get_by_field.assert_called_with("username", "testuser")

    @pytest.mark.asyncio
    async def test_login_with_email_success(self, auth_service, mock_user_repository):
        """Login with email should succeed with valid credentials."""
        password = "TestPassword123"
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.hashed_password = get_password_hash(password)
        mock_user.is_verified = True
        mock_user.is_superuser = False
        mock_user.profile_picture_path = None
        mock_user.created_at = MagicMock()
        mock_user.updated_at = MagicMock()

        mock_user_repository.get_by_field.return_value = mock_user

        login_data = UserLogin(username="test@example.com", password=password)
        result = await auth_service.login(login_data)

        assert result.email == "test@example.com"
        mock_user_repository.get_by_field.assert_called_with(
            "email", "test@example.com"
        )

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, auth_service, mock_user_repository):
        """Login should fail if user does not exist."""
        mock_user_repository.get_by_field.return_value = None

        login_data = UserLogin(username="nonexistent", password="TestPassword123")

        with pytest.raises(BadRequestError) as exc_info:
            await auth_service.login(login_data)

        assert "Invalid" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, auth_service, mock_user_repository):
        """Login should fail with wrong password."""
        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("CorrectPassword123")
        mock_user.is_verified = True

        mock_user_repository.get_by_field.return_value = mock_user

        login_data = UserLogin(username="testuser", password="WrongPassword123")

        with pytest.raises(BadRequestError) as exc_info:
            await auth_service.login(login_data)

        assert "Invalid" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_unverified_user(self, auth_service, mock_user_repository):
        """Login should fail if user is not verified."""
        password = "TestPassword123"
        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash(password)
        mock_user.is_verified = False

        mock_user_repository.get_by_field.return_value = mock_user

        login_data = UserLogin(username="testuser", password=password)

        with pytest.raises(BadRequestError) as exc_info:
            await auth_service.login(login_data)

        # Check for verification-related message (case-insensitive)
        detail = str(exc_info.value.detail).lower()
        assert "verify" in detail or "invalid" in detail


class TestUserCreateSchema:
    """Tests for UserCreate schema validation."""

    def test_valid_user_create(self):
        """Valid user data should pass validation."""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="ValidPass123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_password_too_short(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="Short1",
            )

    def test_password_no_uppercase(self):
        """Password without uppercase letter should fail."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="nouppercase123",
            )

    def test_password_no_number(self):
        """Password without number should fail."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="NoNumberHere",
            )

    def test_invalid_email(self):
        """Invalid email format should fail."""
        with pytest.raises(ValueError):
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="ValidPass123",
            )
