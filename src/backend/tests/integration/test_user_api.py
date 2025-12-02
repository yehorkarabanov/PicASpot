"""
Example integration tests for User API endpoints.

These tests verify that the User endpoints work correctly with
a real database connection.
"""

import pytest
from httpx import AsyncClient

from tests.factories import UserFactory


@pytest.mark.integration
class TestUserRegistration:
    """Test user registration endpoints."""

    @pytest.mark.asyncio
    async def test_register_new_user(
        self,
        async_client: AsyncClient,
        clean_database,
    ):
        """Test successful user registration."""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
        )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data  # Password should not be returned
        assert data["is_verified"] is False  # New users are unverified

    @pytest.mark.asyncio
    async def test_register_duplicate_username(
        self,
        async_client: AsyncClient,
        test_session,
        clean_database,
    ):
        """Test registration with duplicate username fails."""
        # Create existing user
        existing_user = await UserFactory.create(
            test_session,
            username="existinguser",
        )

        # Try to register with same username
        user_data = {
            "username": existing_user.username,
            "email": "newemail@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
        )

        assert response.status_code == 400
        data = response.json()
        assert "username" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        async_client: AsyncClient,
        test_session,
        clean_database,
    ):
        """Test registration with duplicate email fails."""
        # Create existing user
        existing_user = await UserFactory.create(
            test_session,
            email="existing@example.com",
        )

        # Try to register with same email
        user_data = {
            "username": "newusername",
            "email": existing_user.email,
            "password": "SecurePassword123!",
        }

        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
        )

        assert response.status_code == 400
        data = response.json()
        assert "email" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(
        self,
        async_client: AsyncClient,
        clean_database,
    ):
        """Test registration with invalid email format fails."""
        user_data = {
            "username": "newuser",
            "email": "invalid-email",
            "password": "SecurePassword123!",
        }

        response = await async_client.post(
            "/api/v1/auth/register",
            json=user_data,
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.integration
class TestUserLogin:
    """Test user login endpoints."""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        async_client: AsyncClient,
        test_session,
        clean_database,
    ):
        """Test successful user login."""
        # Create verified user
        user = await UserFactory.create_verified_user(
            test_session,
            username="testuser",
            password="testpassword123",
        )

        login_data = {
            "username": user.username,
            "password": "testpassword123",
        }

        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,  # OAuth2 uses form data
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        async_client: AsyncClient,
        test_session,
        clean_database,
    ):
        """Test login with wrong password fails."""
        user = await UserFactory.create_verified_user(
            test_session,
            username="testuser",
            password="correctpassword",
        )

        login_data = {
            "username": user.username,
            "password": "wrongpassword",
        }

        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(
        self,
        async_client: AsyncClient,
        clean_database,
    ):
        """Test login with non-existent username fails."""
        login_data = {
            "username": "nonexistentuser",
            "password": "somepassword",
        }

        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_unverified_user(
        self,
        async_client: AsyncClient,
        test_session,
        clean_database,
    ):
        """Test login with unverified user (depends on app policy)."""
        user = await UserFactory.create_unverified_user(
            test_session,
            username="unverifieduser",
            password="testpassword123",
        )

        login_data = {
            "username": user.username,
            "password": "testpassword123",
        }

        response = await async_client.post(
            "/api/v1/auth/login",
            data=login_data,
        )

        # This behavior depends on your app's requirements
        # You may allow or deny unverified user login
        assert response.status_code in [200, 403]


@pytest.mark.integration
class TestUserProfile:
    """Test user profile endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ):
        """Test getting current user profile."""
        response = await authenticated_client.get("/api/v1/users/me")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_user.id)
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(
        self,
        async_client: AsyncClient,
    ):
        """Test getting current user without authentication fails."""
        response = await async_client.get("/api/v1/users/me")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_current_user(
        self,
        authenticated_client: AsyncClient,
        test_user,
    ):
        """Test updating current user profile."""
        update_data = {
            "username": "updatedusername",
        }

        response = await authenticated_client.patch(
            "/api/v1/users/me",
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == update_data["username"]


# Run these tests with: pytest tests/integration/test_user_api.py -v
