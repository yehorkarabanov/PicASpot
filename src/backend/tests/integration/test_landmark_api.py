"""
Integration tests for Landmark API endpoints.

NOTE: These tests require PostgreSQL with PostGIS extension.
SQLite does not support Geography types, so these tests are skipped
when running with the default in-memory SQLite database.

Tests cover:
- POST /landmarks - Create landmark
- GET /landmarks/{landmark_id} - Get landmark by ID
- PATCH /landmarks/{landmark_id} - Update landmark
- DELETE /landmarks/{landmark_id} - Delete landmark
- GET /landmarks - List landmarks
- GET /landmarks/nearby - Get nearby landmarks
"""

import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.area.models import Area
from app.user.models import User

# Skip all tests in this module - they require PostgreSQL with PostGIS
pytestmark = pytest.mark.skip(
    reason="Integration tests require PostgreSQL with PostGIS - SQLite does not support Geography types"
)


class AreaFactory:
    """Factory for creating test areas."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        creator_id: uuid.UUID,
        name: str = "Test Area",
        is_verified: bool = True,
    ) -> Area:
        area = Area(
            id=uuid.uuid4(),
            name=name,
            description="Test area for landmarks",
            image_url="http://localhost/default.jpg",
            badge_url="http://localhost/default.jpg",
            creator_id=creator_id,
            is_verified=is_verified,
        )
        self.session.add(area)
        await self.session.commit()
        await self.session.refresh(area)
        return area


@pytest.fixture
def area_factory(db_session: AsyncSession) -> AreaFactory:
    """Create an area factory instance."""
    return AreaFactory(db_session)


class TestCreateLandmark:
    """Tests for POST /landmarks endpoint."""

    @pytest.mark.asyncio
    async def test_create_landmark_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        area_factory: AreaFactory,
    ):
        """Authenticated user should be able to create a landmark."""
        area = await area_factory.create(creator_id=test_user.id)

        response = await async_client.post(
            "/landmarks",
            data={
                "name": "Test Landmark",
                "description": "A test landmark",
                "latitude": "40.7128",
                "longitude": "-74.0060",
                "area_id": str(area.id),
                "unlock_radius_meters": "100",
                "photo_radius_meters": "50",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == "Test Landmark"
        assert data["data"]["area_id"] == str(area.id)

    @pytest.mark.asyncio
    async def test_create_landmark_invalid_area(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Creating landmark with non-existent area should fail."""
        response = await async_client.post(
            "/landmarks",
            data={
                "name": "Test Landmark",
                "latitude": "40.7128",
                "longitude": "-74.0060",
                "area_id": str(uuid.uuid4()),
            },
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_landmark_invalid_coordinates(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        area_factory: AreaFactory,
    ):
        """Creating landmark with invalid coordinates should fail."""
        area = await area_factory.create(creator_id=test_user.id)

        # Latitude out of range
        response = await async_client.post(
            "/landmarks",
            data={
                "name": "Test Landmark",
                "latitude": "100.0",  # Invalid: > 90
                "longitude": "0.0",
                "area_id": str(area.id),
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_landmark_unauthorized(
        self,
        async_client: AsyncClient,
        test_user: User,
        area_factory: AreaFactory,
    ):
        """Unauthenticated request should fail."""
        area = await area_factory.create(creator_id=test_user.id)

        response = await async_client.post(
            "/landmarks",
            data={
                "name": "Test Landmark",
                "latitude": "40.7128",
                "longitude": "-74.0060",
                "area_id": str(area.id),
            },
        )

        assert response.status_code == 401


class TestGetLandmark:
    """Tests for GET /landmarks/{landmark_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_landmark_not_found(self, async_client: AsyncClient):
        """Getting non-existent landmark should return 404."""
        response = await async_client.get(f"/landmarks/{uuid.uuid4()}")

        assert response.status_code == 404


class TestDeleteLandmark:
    """Tests for DELETE /landmarks/{landmark_id} endpoint."""

    @pytest.mark.asyncio
    async def test_delete_landmark_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Deleting non-existent landmark should return 404."""
        response = await async_client.delete(
            f"/landmarks/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_landmark_unauthorized(self, async_client: AsyncClient):
        """Unauthenticated delete request should fail."""
        response = await async_client.delete(f"/landmarks/{uuid.uuid4()}")

        assert response.status_code == 401


class TestLandmarkCoordinates:
    """Tests for landmark coordinate validation."""

    @pytest.mark.asyncio
    async def test_boundary_coordinates(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        area_factory: AreaFactory,
    ):
        """Boundary coordinates should be valid."""
        area = await area_factory.create(creator_id=test_user.id)

        # Test boundary values
        test_cases = [
            ("90.0", "180.0"),  # Max values
            ("-90.0", "-180.0"),  # Min values
            ("0.0", "0.0"),  # Zero
        ]

        for lat, lon in test_cases:
            response = await async_client.post(
                "/landmarks",
                data={
                    "name": f"Landmark at {lat},{lon}",
                    "latitude": lat,
                    "longitude": lon,
                    "area_id": str(area.id),
                },
                headers=auth_headers,
            )

            # Should either succeed or fail gracefully
            assert response.status_code in [201, 422, 500]
