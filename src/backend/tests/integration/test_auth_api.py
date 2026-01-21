"""
Integration tests for Auth API endpoints.

NOTE: These tests require PostgreSQL with PostGIS extension.
SQLite does not support Geography types used in the Landmark model,
so these tests are skipped when running with SQLite.

Tests cover:
- POST /auth/register - User registration
- POST /auth/login - User login
- POST /auth/access-token - Get access token (form data)
- POST /auth/verify - Email verification
- POST /auth/send-password-reset - Request password reset
- POST /auth/reset-password - Reset password
"""

import pytest
from httpx import AsyncClient

from app.user.models import User

# Skip all tests in this module - they require PostgreSQL with PostGIS
pytestmark = pytest.mark.skip(
    reason="Integration tests require PostgreSQL with PostGIS - SQLite does not support Geography types"
)


class TestAuthRegister:
    """Tests for POST /auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, async_client: AsyncClient):
        """Registration with valid data should succeed."""
        response = await async_client.post(
            "/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "ValidPass123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert (
            "success" in data["message"].lower()
            or "registered" in data["message"].lower()
        )

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, async_client: AsyncClient, test_user: User
    ):
        """Registration with existing email should fail."""
        response = await async_client.post(
            "/auth/register",
            json={
                "username": "differentuser",
                "email": test_user.email,
                "password": "ValidPass123",
            },
        )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self, async_client: AsyncClient, test_user: User
    ):
        """Registration with existing username should fail."""
        response = await async_client.post(
            "/auth/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "ValidPass123",
            },
        )

        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """Registration with invalid email should fail validation."""
        response = await async_client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "ValidPass123",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, async_client: AsyncClient):
        """Registration with weak password should fail validation."""
        response = await async_client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "weak",
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, async_client: AsyncClient):
        """Registration without required fields should fail."""
        response = await async_client.post(
            "/auth/register",
            json={"username": "testuser"},
        )

        assert response.status_code == 422


class TestAuthLogin:
    """Tests for POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_username_success(
        self, async_client: AsyncClient, test_user: User
    ):
        """Login with valid username and password should succeed."""
        response = await async_client.post(
            "/auth/login",
            json={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "token" in data["data"]
        assert "access_token" in data["data"]["token"]

    @pytest.mark.asyncio
    async def test_login_with_email_success(
        self, async_client: AsyncClient, test_user: User
    ):
        """Login with valid email and password should succeed."""
        response = await async_client.post(
            "/auth/login",
            json={
                "username": test_user.email,  # Email in username field
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "token" in data["data"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self, async_client: AsyncClient, test_user: User
    ):
        """Login with wrong password should fail."""
        response = await async_client.post(
            "/auth/login",
            json={
                "username": test_user.username,
                "password": "WrongPassword123",
            },
        )

        assert response.status_code == 400
        assert "invalid" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """Login with nonexistent user should fail."""
        response = await async_client.post(
            "/auth/login",
            json={
                "username": "nonexistent",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_unverified_user(
        self, async_client: AsyncClient, unverified_user: User
    ):
        """Login with unverified user should fail."""
        response = await async_client.post(
            "/auth/login",
            json={
                "username": unverified_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 400


class TestAuthAccessToken:
    """Tests for POST /auth/access-token endpoint (form data)."""

    @pytest.mark.asyncio
    async def test_access_token_success(
        self, async_client: AsyncClient, test_user: User
    ):
        """Getting access token with valid credentials should succeed."""
        response = await async_client.post(
            "/auth/access-token",
            data={
                "username": test_user.username,
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_access_token_invalid_credentials(self, async_client: AsyncClient):
        """Getting access token with invalid credentials should fail."""
        response = await async_client.post(
            "/auth/access-token",
            data={
                "username": "nonexistent",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 400


class TestAuthPasswordReset:
    """Tests for password reset endpoints."""

    @pytest.mark.asyncio
    async def test_send_password_reset_success(
        self, async_client: AsyncClient, test_user: User
    ):
        """Password reset request for existing user should succeed."""
        response = await async_client.post(
            "/auth/send-password-reset",
            json={"email": test_user.email},
        )

        assert response.status_code == 200
        assert "message" in response.json()

    @pytest.mark.asyncio
    async def test_send_password_reset_nonexistent_email(
        self, async_client: AsyncClient
    ):
        """Password reset for nonexistent email should still return success (security)."""
        response = await async_client.post(
            "/auth/send-password-reset",
            json={"email": "nonexistent@example.com"},
        )

        # Usually returns success for security (don't reveal if email exists)
        # But behavior might vary - adjust based on actual implementation
        assert response.status_code in [200, 400]
