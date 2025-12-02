"""
FastAPI application test fixtures.

This module provides fixtures for the FastAPI application and HTTP clients.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_async_session
from app.main import app


@pytest_asyncio.fixture
async def test_app(test_session: AsyncSession):
    """
    Create FastAPI application with test dependencies.

    This fixture overrides the database session dependency to use the
    test session, ensuring all API requests use the test database.
    """

    # Override database session dependency
    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    yield app

    # Cleanup: Remove overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.

    This client makes HTTP requests to the FastAPI application without
    starting an actual server. Perfect for integration and E2E tests.

    Usage:
        async def test_endpoint(async_client):
            response = await async_client.get("/api/v1/health")
            assert response.status_code == 200
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> AsyncClient:
    """
    Create an authenticated HTTP client.

    This client includes authentication headers in all requests,
    making it easy to test protected endpoints.

    Usage:
        async def test_protected_endpoint(authenticated_client):
            response = await authenticated_client.get("/api/v1/users/me")
            assert response.status_code == 200
    """
    async_client.headers.update(auth_headers)
    return async_client


@pytest_asyncio.fixture
async def superuser_client(
    async_client: AsyncClient, superuser_auth_headers: dict[str, str]
) -> AsyncClient:
    """
    Create an authenticated HTTP client with superuser privileges.

    This client is authenticated as a superuser, useful for testing
    admin-only endpoints.
    """
    async_client.headers.update(superuser_auth_headers)
    return async_client


__all__ = ["test_app", "async_client", "authenticated_client", "superuser_client"]
