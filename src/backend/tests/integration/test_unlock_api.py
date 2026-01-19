"""
Integration tests for Unlock API endpoints.

NOTE: These tests require PostgreSQL with PostGIS extension.
SQLite does not support Geography types, so these tests are skipped
when running with the default in-memory SQLite database.

Tests cover:
- POST /unlocks - Create unlock (photo verification)
- GET /unlocks - List user's unlocks
- GET /unlocks/{unlock_id} - Get unlock by ID
- GET /attempts - List user's attempts
"""

import io
import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.area.models import Area
from app.user.models import User

# Skip all tests in this module - they require PostgreSQL with PostGIS
pytestmark = pytest.mark.skip(reason="Integration tests require PostgreSQL with PostGIS - SQLite does not support Geography types")


class TestCreateUnlock:
    """Tests for POST /unlocks endpoint."""

    @pytest.mark.asyncio
    async def test_create_unlock_unauthorized(self, async_client: AsyncClient):
        """Unauthenticated unlock request should fail."""
        # Create minimal fake image
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        response = await async_client.post(
            "/unlocks",
            data={"landmark_id": str(uuid.uuid4())},
            files={"image_file": ("test.png", io.BytesIO(image_data), "image/png")},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_unlock_invalid_landmark(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Unlock with non-existent landmark should fail."""
        image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        response = await async_client.post(
            "/unlocks",
            data={"landmark_id": str(uuid.uuid4())},
            files={"image_file": ("test.png", io.BytesIO(image_data), "image/png")},
            headers=auth_headers,
        )

        assert response.status_code == 404


class TestListUnlocks:
    """Tests for GET /unlocks endpoint."""

    @pytest.mark.asyncio
    async def test_list_unlocks_unauthorized(self, async_client: AsyncClient):
        """Unauthenticated list request should fail."""
        response = await async_client.get("/unlocks")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_unlocks_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """User with no unlocks should get empty list."""
        response = await async_client.get("/unlocks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["unlocks"] == []


class TestGetUnlock:
    """Tests for GET /unlocks/{unlock_id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_unlock_not_found(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """Getting non-existent unlock should return 404."""
        response = await async_client.get(
            f"/unlocks/{uuid.uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_unlock_unauthorized(self, async_client: AsyncClient):
        """Unauthenticated get request should fail."""
        response = await async_client.get(f"/unlocks/{uuid.uuid4()}")

        assert response.status_code == 401


class TestListAttempts:
    """Tests for GET /attempts endpoint."""

    @pytest.mark.asyncio
    async def test_list_attempts_unauthorized(self, async_client: AsyncClient):
        """Unauthenticated list request should fail."""
        response = await async_client.get("/unlocks/attempts")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_list_attempts_empty(
        self, async_client: AsyncClient, auth_headers: dict
    ):
        """User with no attempts should get empty list."""
        response = await async_client.get("/unlocks/attempts", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
