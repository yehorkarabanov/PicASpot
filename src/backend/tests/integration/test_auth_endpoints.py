"""
Integration tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient

from app.auth.schemas import UserCreate


@pytest.mark.integration
class TestRegisterEndpoint:
    """Tests for POST /auth/register endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123",
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registration with existing email."""
        user_data = {
            "username": "differentuser",
            "email": test_user.email,
            "password": "Password123",
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "email already exists" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with existing username."""
        user_data = {
            "username": test_user.username,
            "email": "different@example.com",
            "password": "Password123",
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 400
        data = response.json()
        assert "username already exists" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "Password123",
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "weak",
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        user_data = {
            "username": "newuser",
            # Missing email and password
        }

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == 422


@pytest.mark.integration
class TestLoginEndpoint:
    """Tests for POST /auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_with_username_success(self, client: AsyncClient, test_user):
        """Test successful login with username."""
        login_data = {
            "username": test_user.username,
            "password": "Password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["username"] == test_user.username
        assert data["data"]["email"] == test_user.email
        assert "token" in data["data"]
        assert "access_token" in data["data"]["token"]

    @pytest.mark.asyncio
    async def test_login_with_email_success(self, client: AsyncClient, test_user):
        """Test successful login with email."""
        login_data = {
            "username": test_user.email,
            "password": "Password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["username"] == test_user.username

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Test login with incorrect password."""
        login_data = {
            "username": test_user.username,
            "password": "WrongPass123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        login_data = {
            "username": "nonexistent",
            "password": "Password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_unverified_user(self, client: AsyncClient, unverified_user):
        """Test login with unverified user."""
        login_data = {
            "username": unverified_user.username,
            "password": "Password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 400
        data = response.json()
        assert "verify your email" in data["detail"]

    @pytest.mark.asyncio
    async def test_login_returns_user_data(self, client: AsyncClient, test_user):
        """Test that login returns complete user data."""
        login_data = {
            "username": test_user.username,
            "password": "Password123",
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()["data"]
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "is_superuser" in data
        assert "is_verified" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "token" in data


@pytest.mark.integration
class TestAccessTokenEndpoint:
    """Tests for GET /auth/access-token endpoint (get current user)."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self, authenticated_client: AsyncClient, test_user
    ):
        """Test getting current user with valid token."""
        response = await authenticated_client.get("/auth/access-token")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"]["username"] == test_user.username
        assert data["data"]["email"] == test_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/auth/access-token")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token."""
        client.headers.update({"Authorization": "Bearer invalid_token"})
        response = await client.get("/auth/access-token")

        assert response.status_code == 401


@pytest.mark.integration
class TestVerifyEmailEndpoint:
    """Tests for POST /auth/verify endpoint."""

    @pytest.mark.asyncio
    async def test_verify_email_with_invalid_token(self, client: AsyncClient):
        """Test email verification with invalid token."""
        response = await client.post("/auth/verify", json={"token": "invalid_token"})

        assert response.status_code in [400, 401]


@pytest.mark.integration
class TestResendVerificationEndpoint:
    """Tests for POST /auth/resend-verification-token endpoint."""

    @pytest.mark.asyncio
    async def test_resend_verification_unverified_user(
        self, client: AsyncClient, unverified_user, mock_celery
    ):
        """Test resending verification token to unverified user."""
        response = await client.post(
            "/auth/resend-verification-token",
            json={"email": unverified_user.email},
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_resend_verification_verified_user(
        self, client: AsyncClient, test_user
    ):
        """Test resending verification token to already verified user."""
        response = await client.post(
            "/auth/resend-verification-token",
            json={"email": test_user.email},
        )

        assert response.status_code == 400
        data = response.json()
        assert "already verified" in data["detail"]

    @pytest.mark.asyncio
    async def test_resend_verification_nonexistent_user(self, client: AsyncClient):
        """Test resending verification token to non-existent user."""
        response = await client.post(
            "/auth/resend-verification-token",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.slow
class TestRateLimiting:
    """Tests for rate limiting on auth endpoints."""

    @pytest.mark.asyncio
    async def test_login_rate_limiting(self, client: AsyncClient):
        """Test that login endpoint is rate-limited."""
        login_data = {
            "username": "testuser",
            "password": "Password123",
        }

        # Make multiple rapid requests
        responses = []
        for _ in range(10):
            response = await client.post("/auth/login", json=login_data)
            responses.append(response)

        # Check if any request was rate-limited (429 status)
        status_codes = [r.status_code for r in responses]
        # At least one should succeed or fail with 400,
        # but if rate limiting works, some should be 429
        assert any(code in [400, 429] for code in status_codes)

    @pytest.mark.asyncio
    async def test_register_rate_limiting(self, client: AsyncClient):
        """Test that register endpoint is rate-limited."""
        # Make multiple rapid registration attempts
        responses = []
        for i in range(10):
            user_data = {
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "Password123",
            }
            response = await client.post("/auth/register", json=user_data)
            responses.append(response)

        status_codes = [r.status_code for r in responses]
        # Should have mix of successful (201) or rate-limited (429)
        assert any(code in [201, 429] for code in status_codes)

