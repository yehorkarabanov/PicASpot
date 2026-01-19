"""
Unit tests for LandmarkService.

Tests cover:
- Create landmark
- Get landmark by ID
- Update landmark
- Delete landmark
- Permission checks
- Location handling
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

import pytest

from app.area.repository import AreaRepository
from app.core.exceptions import ForbiddenError, NotFoundError
from app.landmark.repository import LandmarkRepository
from app.landmark.service import LandmarkService
from app.user.models import User


class TestLandmarkServiceCreate:
    """Tests for LandmarkService.create_landmark method."""

    @pytest.fixture
    def mock_landmark_repository(self):
        """Create a mock landmark repository."""
        return AsyncMock(spec=LandmarkRepository)

    @pytest.fixture
    def mock_area_repository(self):
        """Create a mock area repository."""
        return AsyncMock(spec=AreaRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        mock = AsyncMock()
        mock.upload_file = AsyncMock(
            return_value={
                "object_path": "landmarks/test.jpg",
                "public_url": "http://localhost/minio/landmarks/test.jpg",
            }
        )
        return mock

    @pytest.fixture
    def landmark_service(
        self, mock_landmark_repository, mock_area_repository, mock_storage_service
    ):
        """Create a LandmarkService instance with mocked dependencies."""
        return LandmarkService(
            landmark_repository=mock_landmark_repository,
            area_repository=mock_area_repository,
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
    async def test_create_landmark_success(
        self,
        landmark_service,
        mock_landmark_repository,
        mock_area_repository,
        regular_user,
    ):
        """Landmark creation should succeed with valid data."""
        area_id = uuid.uuid4()
        landmark_id = uuid.uuid4()

        # Mock area exists
        mock_area = MagicMock()
        mock_area.id = area_id
        mock_area_repository.get_by_id.return_value = mock_area

        # Mock landmark creation
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.name = "Test Landmark"
        mock_landmark.description = "Test Description"
        mock_landmark.image_url = "http://localhost/default.jpg"
        mock_landmark.hint_image_url = None
        mock_landmark.area_id = area_id
        mock_landmark.creator_id = regular_user.id
        mock_landmark.unlock_radius_meters = 100
        mock_landmark.photo_radius_meters = 50
        mock_landmark.photo_location_radius = None
        mock_landmark.created_at = datetime.now(timezone.utc)
        mock_landmark.updated_at = datetime.now(timezone.utc)

        # Mock geography properties
        mock_landmark.latitude = 40.7128
        mock_landmark.longitude = -74.0060
        mock_landmark.photo_latitude = None
        mock_landmark.photo_longitude = None

        mock_landmark_repository.create.return_value = mock_landmark

        # Create landmark data
        landmark_data = MagicMock()
        landmark_data.name = "Test Landmark"
        landmark_data.description = "Test Description"
        landmark_data.area_id = area_id
        landmark_data.latitude = 40.7128
        landmark_data.longitude = -74.0060
        landmark_data.unlock_radius_meters = 100
        landmark_data.photo_radius_meters = 50
        landmark_data.photo_latitude = None
        landmark_data.photo_longitude = None
        landmark_data.image_file = None
        landmark_data.hint_image_file = None
        landmark_data.model_dump = MagicMock(
            return_value={
                "name": "Test Landmark",
                "description": "Test Description",
                "area_id": area_id,
                "unlock_radius_meters": 100,
                "photo_radius_meters": 50,
            }
        )

        result = await landmark_service.create_landmark(landmark_data, regular_user)

        assert result.name == "Test Landmark"
        mock_landmark_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_landmark_area_not_found(
        self, landmark_service, mock_area_repository, regular_user
    ):
        """Landmark creation should fail if area does not exist."""
        area_id = uuid.uuid4()
        mock_area_repository.get_by_id.return_value = None

        landmark_data = MagicMock()
        landmark_data.area_id = area_id

        with pytest.raises(NotFoundError) as exc_info:
            await landmark_service.create_landmark(landmark_data, regular_user)

        assert "not found" in str(exc_info.value.detail).lower()


class TestLandmarkServiceGet:
    """Tests for LandmarkService.get_landmark method."""

    @pytest.fixture
    def mock_landmark_repository(self):
        """Create a mock landmark repository."""
        return AsyncMock(spec=LandmarkRepository)

    @pytest.fixture
    def mock_area_repository(self):
        """Create a mock area repository."""
        return AsyncMock(spec=AreaRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        return AsyncMock()

    @pytest.fixture
    def landmark_service(
        self, mock_landmark_repository, mock_area_repository, mock_storage_service
    ):
        """Create a LandmarkService instance with mocked dependencies."""
        return LandmarkService(
            landmark_repository=mock_landmark_repository,
            area_repository=mock_area_repository,
            storage=mock_storage_service,
            timezone=ZoneInfo("UTC"),
        )

    @pytest.mark.asyncio
    async def test_get_landmark_success(
        self, landmark_service, mock_landmark_repository
    ):
        """Get landmark should return landmark data when it exists."""
        landmark_id = uuid.uuid4()
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.name = "Test Landmark"
        mock_landmark.description = "Description"
        mock_landmark.image_url = "http://localhost/image.jpg"
        mock_landmark.hint_image_url = None
        mock_landmark.area_id = uuid.uuid4()
        mock_landmark.creator_id = uuid.uuid4()
        mock_landmark.unlock_radius_meters = 100
        mock_landmark.photo_radius_meters = 50
        mock_landmark.photo_location_radius = None
        mock_landmark.latitude = 40.7128
        mock_landmark.longitude = -74.0060
        mock_landmark.photo_latitude = None
        mock_landmark.photo_longitude = None
        mock_landmark.created_at = datetime.now(timezone.utc)
        mock_landmark.updated_at = datetime.now(timezone.utc)

        mock_landmark_repository.get_by_id.return_value = mock_landmark

        result = await landmark_service.get_landmark(landmark_id)

        assert result.id == landmark_id
        assert result.name == "Test Landmark"

    @pytest.mark.asyncio
    async def test_get_landmark_not_found(
        self, landmark_service, mock_landmark_repository
    ):
        """Get landmark should raise NotFoundError when landmark does not exist."""
        mock_landmark_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await landmark_service.get_landmark(uuid.uuid4())

        assert "not found" in str(exc_info.value.detail).lower()


class TestLandmarkServiceDelete:
    """Tests for LandmarkService.delete_landmark method."""

    @pytest.fixture
    def mock_landmark_repository(self):
        """Create a mock landmark repository."""
        return AsyncMock(spec=LandmarkRepository)

    @pytest.fixture
    def mock_area_repository(self):
        """Create a mock area repository."""
        return AsyncMock(spec=AreaRepository)

    @pytest.fixture
    def mock_storage_service(self):
        """Create a mock storage service."""
        return AsyncMock()

    @pytest.fixture
    def landmark_service(
        self, mock_landmark_repository, mock_area_repository, mock_storage_service
    ):
        """Create a LandmarkService instance with mocked dependencies."""
        return LandmarkService(
            landmark_repository=mock_landmark_repository,
            area_repository=mock_area_repository,
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

    @pytest.fixture
    def admin_user(self):
        """Create an admin user mock."""
        user = MagicMock(spec=User)
        user.id = uuid.uuid4()
        user.username = "adminuser"
        user.is_superuser = True
        return user

    @pytest.mark.asyncio
    async def test_delete_own_landmark(
        self, landmark_service, mock_landmark_repository, regular_user
    ):
        """User should be able to delete their own landmark."""
        landmark_id = uuid.uuid4()
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.name = "My Landmark"
        mock_landmark.creator_id = regular_user.id

        mock_landmark_repository.get_by_id.return_value = mock_landmark
        mock_landmark_repository.delete.return_value = True

        await landmark_service.delete_landmark(landmark_id, regular_user)

        mock_landmark_repository.delete.assert_called_once_with(landmark_id)

    @pytest.mark.asyncio
    async def test_delete_other_users_landmark_forbidden(
        self, landmark_service, mock_landmark_repository, regular_user
    ):
        """Regular user should not be able to delete another user's landmark."""
        landmark_id = uuid.uuid4()
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.creator_id = uuid.uuid4()  # Different user

        mock_landmark_repository.get_by_id.return_value = mock_landmark

        with pytest.raises(ForbiddenError) as exc_info:
            await landmark_service.delete_landmark(landmark_id, regular_user)

        assert "permission" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_admin_can_delete_any_landmark(
        self, landmark_service, mock_landmark_repository, admin_user
    ):
        """Admin should be able to delete any landmark."""
        landmark_id = uuid.uuid4()
        mock_landmark = MagicMock()
        mock_landmark.id = landmark_id
        mock_landmark.name = "Other User Landmark"
        mock_landmark.creator_id = uuid.uuid4()  # Different user

        mock_landmark_repository.get_by_id.return_value = mock_landmark
        mock_landmark_repository.delete.return_value = True

        await landmark_service.delete_landmark(landmark_id, admin_user)

        mock_landmark_repository.delete.assert_called_once_with(landmark_id)

    @pytest.mark.asyncio
    async def test_delete_landmark_not_found(
        self, landmark_service, mock_landmark_repository, regular_user
    ):
        """Delete should raise NotFoundError when landmark does not exist."""
        mock_landmark_repository.get_by_id.return_value = None

        with pytest.raises(NotFoundError) as exc_info:
            await landmark_service.delete_landmark(uuid.uuid4(), regular_user)

        assert "not found" in str(exc_info.value.detail).lower()


class TestLandmarkCoordinateValidation:
    """Tests for landmark coordinate validation."""

    def test_valid_coordinates(self):
        """Valid coordinates should pass validation."""
        from app.landmark.schemas import LandmarkBase

        landmark = LandmarkBase(
            name="Test",
            latitude=40.7128,
            longitude=-74.0060,
        )
        assert landmark.latitude == 40.7128
        assert landmark.longitude == -74.0060

    def test_latitude_out_of_range_high(self):
        """Latitude above 90 should fail validation."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=91.0,
                longitude=0.0,
            )

    def test_latitude_out_of_range_low(self):
        """Latitude below -90 should fail validation."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=-91.0,
                longitude=0.0,
            )

    def test_longitude_out_of_range_high(self):
        """Longitude above 180 should fail validation."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=181.0,
            )

    def test_longitude_out_of_range_low(self):
        """Longitude below -180 should fail validation."""
        from app.landmark.schemas import LandmarkBase

        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=-181.0,
            )

    def test_unlock_radius_validation(self):
        """Unlock radius should be within valid range."""
        from app.landmark.schemas import LandmarkBase

        # Valid radius
        landmark = LandmarkBase(
            name="Test",
            latitude=0.0,
            longitude=0.0,
            unlock_radius_meters=500,
        )
        assert landmark.unlock_radius_meters == 500

        # Radius too small
        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=0.0,
                unlock_radius_meters=0,
            )

        # Radius too large
        with pytest.raises(ValueError):
            LandmarkBase(
                name="Test",
                latitude=0.0,
                longitude=0.0,
                unlock_radius_meters=20000,
            )
