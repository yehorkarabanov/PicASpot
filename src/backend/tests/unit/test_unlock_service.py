"""
Unit tests for UnlockService.

Tests cover:
- Create unlock (verification request)
- Handle verification result
- Get unlock by ID
- Permission checks
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from app.core.exceptions import BadRequestError, NotFoundError
from app.landmark.repository import LandmarkRepository
from app.unlock.models import AttemptStatus
from app.unlock.repository import AttemptRepository, UnlockRepository
from app.unlock.service import UnlockService
from app.user.models import User


class TestUnlockServiceCreate:
    """Tests for UnlockService.create_unlock method."""

    @pytest.fixture
    def mock_unlock_repository(self):
        """Create a mock unlock repository."""
        return AsyncMock(spec=UnlockRepository)

    @pytest.fixture
    def mock_attempt_repository(self):
        """Create a mock attempt repository."""
        return AsyncMock(spec=AttemptRepository)

    @pytest.fixture
    def mock_landmark_repository(self):
        """Create a mock landmark repository."""
        return AsyncMock(spec=LandmarkRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        mock = AsyncMock()
        mock.upload_file = AsyncMock(
            return_value={
                "object_path": "unlocks/test.jpg",
                "public_url": "http://localhost/minio/unlocks/test.jpg",
            }
        )
        return mock

    @pytest.fixture
    def unlock_service(
        self,
        mock_unlock_repository,
        mock_attempt_repository,
        mock_landmark_repository,
        mock_storage_service,
    ):
        """Create an UnlockService instance with mocked dependencies."""
        return UnlockService(
            unlock_repository=mock_unlock_repository,
            attempt_repository=mock_attempt_repository,
            landmark_repository=mock_landmark_repository,
            storage=mock_storage_service,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.fixture
    def regular_user(self):
        """Create a regular user mock."""
        user = MagicMock(spec=User)
        user.id = uuid.uuid4()
        user.username = "testuser"
        user.is_superuser = False
        return user

    @pytest.mark.asyncio
    async def test_create_unlock_success(
        self,
        unlock_service,
        mock_landmark_repository,
        mock_attempt_repository,
        regular_user,
    ):
        """Unlock creation should succeed with valid data."""
        landmark_id = uuid.uuid4()
        attempt_id = uuid.uuid4()

        # Mock landmark exists without existing unlock
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.name = "Test Landmark"
        mock_landmark.latitude = 40.7128
        mock_landmark.longitude = -74.0060
        mock_landmark.unlock_radius_meters = 100
        mock_landmark.photo_radius_meters = 50

        mock_landmark_repository.get_landmark_with_unlock_status.return_value = (
            mock_landmark,
            None,  # No existing unlock
        )

        # Mock attempt creation
        mock_attempt = MagicMock()
        mock_attempt.id = attempt_id
        mock_attempt.status = AttemptStatus.PENDING
        mock_attempt_repository.create.return_value = mock_attempt

        # Create unlock data
        unlock_data = MagicMock()
        unlock_data.landmark_id = landmark_id
        unlock_data.image_file = MagicMock()
        unlock_data.image_file.read = AsyncMock(return_value=b"fake image data")
        unlock_data.image_file.filename = "test.jpg"
        unlock_data.image_file.content_type = "image/jpeg"

        with patch("app.unlock.service.kafka_producer") as mock_kafka:
            mock_kafka.send_unlock_verify_message = AsyncMock()
            await unlock_service.create_unlock(unlock_data, regular_user)

        mock_attempt_repository.create.assert_called_once()
        mock_kafka.send_unlock_verify_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_unlock_landmark_not_found(
        self, unlock_service, mock_landmark_repository, regular_user
    ):
        """Unlock creation should fail if landmark does not exist."""
        mock_landmark_repository.get_landmark_with_unlock_status.return_value = (
            None,
            None,
        )

        unlock_data = MagicMock()
        unlock_data.landmark_id = uuid.uuid4()

        with pytest.raises(NotFoundError) as exc_info:
            await unlock_service.create_unlock(unlock_data, regular_user)

        assert "not found" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_create_unlock_already_unlocked(
        self, unlock_service, mock_landmark_repository, regular_user
    ):
        """Unlock creation should fail if landmark is already unlocked."""
        landmark_id = uuid.uuid4()

        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id

        existing_unlock = MagicMock()  # Landmark already unlocked

        mock_landmark_repository.get_landmark_with_unlock_status.return_value = (
            mock_landmark,
            existing_unlock,
        )

        unlock_data = MagicMock()
        unlock_data.landmark_id = landmark_id

        with pytest.raises(BadRequestError) as exc_info:
            await unlock_service.create_unlock(unlock_data, regular_user)

        assert "already unlocked" in str(exc_info.value.detail).lower()


class TestUnlockServiceHandleVerification:
    """Tests for UnlockService.handle_verification_result method."""

    @pytest.fixture
    def mock_unlock_repository(self):
        """Create a mock unlock repository."""
        return AsyncMock(spec=UnlockRepository)

    @pytest.fixture
    def mock_attempt_repository(self):
        """Create a mock attempt repository."""
        return AsyncMock(spec=AttemptRepository)

    @pytest.fixture
    def mock_landmark_repository(self):
        """Create a mock landmark repository."""
        return AsyncMock(spec=LandmarkRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        return AsyncMock()

    @pytest.fixture
    def unlock_service(
        self,
        mock_unlock_repository,
        mock_attempt_repository,
        mock_landmark_repository,
        mock_storage_service,
    ):
        """Create an UnlockService instance with mocked dependencies."""
        return UnlockService(
            unlock_repository=mock_unlock_repository,
            attempt_repository=mock_attempt_repository,
            landmark_repository=mock_landmark_repository,
            storage=mock_storage_service,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_handle_verification_success(
        self, unlock_service, mock_attempt_repository, mock_unlock_repository
    ):
        """Successful verification should create an unlock."""
        attempt_id = uuid.uuid4()
        user_id = uuid.uuid4()
        landmark_id = uuid.uuid4()

        mock_attempt = MagicMock()
        mock_attempt.id = attempt_id
        mock_attempt.user_id = user_id
        mock_attempt.landmark_id = landmark_id
        mock_attempt.status = AttemptStatus.PENDING
        mock_attempt.similarity_score = None
        mock_attempt.error_message = None

        mock_attempt_repository.get_by_id.return_value = mock_attempt

        await unlock_service.handle_verification_result(
            attempt_id=attempt_id,
            success=True,
            photo_url="http://localhost/photo.jpg",
            similarity_score=0.85,
            error=None,
        )

        mock_unlock_repository.create.assert_called_once()
        mock_attempt_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_verification_failure(
        self, unlock_service, mock_attempt_repository, mock_unlock_repository
    ):
        """Failed verification should update attempt status without creating unlock."""
        attempt_id = uuid.uuid4()
        user_id = uuid.uuid4()
        landmark_id = uuid.uuid4()

        mock_attempt = MagicMock()
        mock_attempt.id = attempt_id
        mock_attempt.user_id = user_id
        mock_attempt.landmark_id = landmark_id
        mock_attempt.status = AttemptStatus.PENDING
        mock_attempt.similarity_score = None
        mock_attempt.error_message = None

        mock_attempt_repository.get_by_id.return_value = mock_attempt

        await unlock_service.handle_verification_result(
            attempt_id=attempt_id,
            success=False,
            photo_url="http://localhost/photo.jpg",
            similarity_score=0.3,
            error=None,
        )

        mock_unlock_repository.create.assert_not_called()
        mock_attempt_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_verification_with_error(
        self, unlock_service, mock_attempt_repository, mock_unlock_repository
    ):
        """Verification with error should update attempt with error message."""
        attempt_id = uuid.uuid4()
        user_id = uuid.uuid4()
        landmark_id = uuid.uuid4()

        mock_attempt = MagicMock()
        mock_attempt.id = attempt_id
        mock_attempt.user_id = user_id
        mock_attempt.landmark_id = landmark_id
        mock_attempt.status = AttemptStatus.PENDING
        mock_attempt.similarity_score = None
        mock_attempt.error_message = None

        mock_attempt_repository.get_by_id.return_value = mock_attempt

        await unlock_service.handle_verification_result(
            attempt_id=attempt_id,
            success=False,
            photo_url="http://localhost/photo.jpg",
            similarity_score=None,
            error="Image processing failed",
        )

        mock_unlock_repository.create.assert_not_called()
        assert mock_attempt.error_message == "Image processing failed"

    @pytest.mark.asyncio
    async def test_handle_verification_attempt_not_found(
        self, unlock_service, mock_attempt_repository
    ):
        """Should handle case where attempt is not found gracefully."""
        mock_attempt_repository.get_by_id.return_value = None

        # Should not raise, just log error
        await unlock_service.handle_verification_result(
            attempt_id=uuid.uuid4(),
            success=True,
            photo_url="http://localhost/photo.jpg",
            similarity_score=0.85,
            error=None,
        )


class TestAttemptStatus:
    """Tests for AttemptStatus enum."""

    def test_attempt_status_values(self):
        """Verify all expected status values exist."""
        assert AttemptStatus.PENDING == "PENDING"
        assert AttemptStatus.SUCCESS == "SUCCESS"
        assert AttemptStatus.FAILED == "FAILED"

    def test_attempt_status_is_string(self):
        """AttemptStatus values should be strings."""
        for status in AttemptStatus:
            assert isinstance(status.value, str)
