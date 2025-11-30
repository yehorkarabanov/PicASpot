"""
Pytest configuration and shared fixtures for PicASpot backend tests.

This module provides fixtures for:
- Test database setup (SQLite in-memory for unit tests)
- Async test client for API testing
- Authenticated client fixtures
- Mock Redis and Celery dependencies
"""

import asyncio
import logging
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import create_access_token, get_password_hash
from app.database.base import Base
from app.database.manager import get_async_session
from app.database.redis import get_redis_client
from app.main import app
from app.user.models import User

# Disable aiosqlite debug logging to avoid formatting issues with SQL PRIMARY keyword
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Initialize Faker for test data generation
fake = Faker()

# Use SQLite in-memory database for fast unit tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create a test database engine with SQLite in-memory."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    async with engine.begin() as conn:
        # Only create tables that don't use PostGIS (for SQLite compatibility)
        # Import models individually to avoid creating landmarks/unlocks tables
        from app.user.models import User
        from app.area.models import Area

        # Create only the tables we need for auth tests
        await conn.run_sync(User.__table__.create, checkfirst=True)
        await conn.run_sync(Area.__table__.create, checkfirst=True)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=0)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
async def mock_celery():
    """Mock Celery tasks for testing."""
    with patch("app.celery.tasks.email_tasks.tasks.user_verify_mail_event") as mock_verify, \
         patch("app.celery.tasks.email_tasks.tasks.user_reset_password_mail_event") as mock_reset:
        mock_verify.delay = MagicMock(return_value=None)
        mock_reset.delay = MagicMock(return_value=None)
        yield {
            "verify_email": mock_verify,
            "reset_password": mock_reset,
        }


@pytest.fixture
async def client(test_session, mock_redis, mock_celery) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden dependencies."""

    async def override_get_async_session():
        yield test_session

    async def override_get_redis():
        return mock_redis

    app.dependency_overrides[get_async_session] = override_get_async_session
    app.dependency_overrides[get_redis_client] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        hashed_password=get_password_hash("Password123"),  # Matches validation: uppercase, digit, 8+ chars
        is_verified=True,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def superuser(test_session: AsyncSession) -> User:
    """Create a superuser in the database."""
    user = User(
        email="admin@test.com",
        username="admin",
        hashed_password=get_password_hash("Admin123"),  # Matches validation
        is_verified=True,
        is_superuser=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def unverified_user(test_session: AsyncSession) -> User:
    """Create an unverified user in the database."""
    user = User(
        email=fake.email(),
        username=fake.user_name(),
        hashed_password=get_password_hash("Password123"),  # Matches validation
        is_verified=False,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
def access_token(test_user: User) -> str:
    """Generate an access token for the test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def superuser_token(superuser: User) -> str:
    """Generate an access token for the superuser."""
    return create_access_token(subject=str(superuser.id))


@pytest.fixture
async def authenticated_client(
    client: AsyncClient, access_token: str
) -> AsyncClient:
    """Create an authenticated test client."""
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client


@pytest.fixture
async def authenticated_superuser_client(
    client: AsyncClient, superuser_token: str
) -> AsyncClient:
    """Create an authenticated superuser test client."""
    client.headers.update({"Authorization": f"Bearer {superuser_token}"})
    return client


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL


