"""
Unit tests for UserService.

Tests cover:
- Get user by ID
- Update user information
- Update password
- Profile picture operations
"""

import uuid
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

import pytest

from app.auth.security import get_password_hash
from app.core.exceptions import BadRequestError, NotFoundError
from app.user.repository import UserRepository
from app.user.schemas import UserUpdate, UserUpdatePassword
from app.user.service import UserService


class TestUserServiceGetUser:
    """Tests for UserService.get_user method."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        mock = AsyncMock()
        mock.get_presigned_url = AsyncMock(
            return_value="http://localhost/presigned/profile.jpg"
        )
        return mock

    @pytest.fixture
    def user_service(self, mock_user_repository, mock_storage_service):
        """Create a UserService instance with mocked dependencies."""
        service = UserService(
            user_repository=mock_user_repository,
            timezone=ZoneInfo("UTC"),
            storage_service=mock_storage_service,
        )
        return service

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user_repository):
        """Get user should raise NotFoundError when user does not exist."""
        mock_user_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.get_user(str(uuid.uuid4()))

        assert "not found" in str(exc_info.value.detail).lower()


class TestUserServiceUpdateUser:
    """Tests for UserService.update_user method."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """Create a UserService instance with mocked dependencies."""
        return UserService(
            user_repository=mock_user_repository,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_update_user_username_taken(self, user_service, mock_user_repository):
        """Update user should fail when username is already taken."""
        user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.username = "oldusername"

        existing_user = MagicMock()
        existing_user.id = other_user_id

        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.get_by_field.return_value = existing_user

        update_data = UserUpdate(username="takenusername")

        with pytest.raises(BadRequestError) as exc_info:
            await user_service.update_user(str(user_id), update_data)

        assert "taken" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service, mock_user_repository):
        """Update user should raise NotFoundError when user does not exist."""
        mock_user_repository.get_by_id.return_value = None

        update_data = UserUpdate(username="newusername")

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.update_user(str(uuid.uuid4()), update_data)

        assert "not found" in str(exc_info.value.detail).lower()


class TestUserServiceUpdatePassword:
    """Tests for UserService.update_password method."""

    @pytest.fixture
    def mock_user_repository(self):
        """Create a mock user repository."""
        return AsyncMock(spec=UserRepository)

    @pytest.fixture
    def user_service(self, mock_user_repository):
        """Create a UserService instance with mocked dependencies."""
        return UserService(
            user_repository=mock_user_repository,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_update_password_success(self, user_service, mock_user_repository):
        """Password update should succeed with correct current password."""
        user_id = uuid.uuid4()
        current_password = "CurrentPass123"

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.hashed_password = get_password_hash(current_password)

        mock_user_repository.get_by_id.return_value = mock_user
        mock_user_repository.save.return_value = mock_user

        password_data = UserUpdatePassword(
            password=current_password,
            new_password="NewPassword123",
        )

        # Should not raise any exception
        await user_service.update_password(str(user_id), password_data)
        mock_user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_password_wrong_current(
        self, user_service, mock_user_repository
    ):
        """Password update should fail with incorrect current password."""
        user_id = uuid.uuid4()

        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.hashed_password = get_password_hash("ActualPassword123")

        mock_user_repository.get_by_id.return_value = mock_user

        password_data = UserUpdatePassword(
            password="WrongPassword123",
            new_password="NewPassword123",
        )

        with pytest.raises(BadRequestError) as exc_info:
            await user_service.update_password(str(user_id), password_data)

        assert "incorrect" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_update_password_user_not_found(
        self, user_service, mock_user_repository
    ):
        """Password update should raise NotFoundError when user does not exist."""
        mock_user_repository.get_by_id.return_value = None

        password_data = UserUpdatePassword(
            password="CurrentPass123",
            new_password="NewPassword123",
        )

        with pytest.raises(NotFoundError) as exc_info:
            await user_service.update_password(str(uuid.uuid4()), password_data)

        assert "not found" in str(exc_info.value.detail).lower()


class TestUserUpdateSchema:
    """Tests for UserUpdate schema validation."""

    def test_valid_update_username(self):
        """Valid username update should pass."""
        update = UserUpdate(username="newusername")
        assert update.username == "newusername"
        assert update.email is None

    def test_valid_update_email(self):
        """Valid email update should pass."""
        update = UserUpdate(email="new@example.com")
        assert update.email == "new@example.com"
        assert update.username is None

    def test_valid_update_both(self):
        """Updating both username and email should pass."""
        update = UserUpdate(username="newuser", email="new@example.com")
        assert update.username == "newuser"
        assert update.email == "new@example.com"

    def test_empty_update(self):
        """Empty update should be valid (no changes)."""
        update = UserUpdate()
        assert update.username is None
        assert update.email is None

    def test_invalid_email_format(self):
        """Invalid email format should fail."""
        with pytest.raises(ValueError):
            UserUpdate(email="invalid-email")


class TestUserUpdatePasswordSchema:
    """Tests for UserUpdatePassword schema validation."""

    def test_valid_password_update(self):
        """Valid password update should pass."""
        update = UserUpdatePassword(
            password="CurrentPass123",
            new_password="NewPassword123",
        )
        assert update.password == "CurrentPass123"
        assert update.new_password == "NewPassword123"

    def test_password_too_short(self):
        """Password shorter than 8 characters should fail."""
        with pytest.raises(ValueError):
            UserUpdatePassword(
                password="Short1",
                new_password="ValidPass123",
            )

    def test_new_password_too_short(self):
        """New password shorter than 8 characters should fail."""
        with pytest.raises(ValueError):
            UserUpdatePassword(
                password="ValidPass123",
                new_password="Short1",
            )
