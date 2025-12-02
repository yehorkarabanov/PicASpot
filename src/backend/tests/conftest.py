"""
Global pytest configuration and fixtures.

This module provides the foundation for all tests, including:
- Test database setup/teardown
- Test Redis setup/teardown
- FastAPI application fixtures
- HTTP client fixtures
- Authentication helpers
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.auth.security import create_access_token, get_password_hash
from app.database.base import Base
from app.database.dependencies import get_async_session
from app.database.redis import get_redis_client, init_redis
from app.main import app
from app.settings import settings
from app.user.models import User

# Initialize Faker for test data generation
fake = Faker()


# ============================================================================
# Pytest Configuration
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create a test database engine for the entire test session.

    This engine connects to a separate test database to avoid
    interfering with development data.
    """
    # Create test database URL
    test_db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}_test"

    # Create engine with test-optimized settings
    engine = create_async_engine(
        url=test_db_url,
        echo=False,  # Disable SQL logging in tests
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: Drop all tables and dispose engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_maker(
    test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """
    Create a session factory for tests.

    This factory creates database sessions that are isolated
    from the main application sessions.
    """
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture
async def test_session(
    test_session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh database session for each test.

    Each test gets a clean session that rolls back all changes
    after the test completes, ensuring test isolation.
    """
    async with test_session_maker() as session:
        async with session.begin():
            yield session
            # Rollback to ensure test isolation
            await session.rollback()


@pytest_asyncio.fixture
async def clean_database(test_session: AsyncSession) -> AsyncGenerator[None, None]:
    """
    Clean database between tests.

    This fixture ensures that each test starts with a clean database state.
    """
    yield
    # Cleanup after test
    await test_session.rollback()

    # Clear all tables
    async with test_session.begin():
        # Delete in order to respect foreign key constraints
        await test_session.execute(text("DELETE FROM unlocks"))
        await test_session.execute(text("DELETE FROM landmarks"))
        await test_session.execute(text("DELETE FROM areas"))
        await test_session.execute(text("DELETE FROM users"))
        await test_session.commit()


# ============================================================================
# Redis Fixtures
# ============================================================================


@pytest_asyncio.fixture(scope="session")
async def test_redis_client():
    """
    Initialize Redis client for tests.

    This uses the same Redis instance but ensures cleanup between tests.
    """
    await init_redis()
    client = await get_redis_client()
    yield client
    # Cleanup is handled by redis_cleanup fixture


@pytest_asyncio.fixture(autouse=True)
async def redis_cleanup():
    """
    Clean Redis data between tests.

    This fixture runs automatically for every test to ensure
    Redis data doesn't leak between tests.
    """
    yield
    # Cleanup after test
    redis_client = await get_redis_client()
    # Flush test-related keys only (tokens, rate limits, etc.)
    async for key in redis_client.scan_iter(match="token:*"):
        await redis_client.delete(key)
    async for key in redis_client.scan_iter(match="rate_limit:*"):
        await redis_client.delete(key)


# ============================================================================
# FastAPI Application Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_app(test_session: AsyncSession):
    """
    Create FastAPI application with test dependencies.

    This overrides the database session dependency to use the test session,
    ensuring all requests use the test database.
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

    This client can make HTTP requests to the FastAPI application
    without actually starting a server.
    """
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        follow_redirects=True,
    ) as client:
        yield client


# ============================================================================
# User Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """
    Create a verified test user.

    This user can be used for authenticated API requests.
    """
    user = User(
        id=uuid.uuid4(),
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash("testpassword123"),
        is_verified=True,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_superuser(test_session: AsyncSession) -> User:
    """
    Create a verified superuser for admin tests.
    """
    user = User(
        id=uuid.uuid4(),
        username=f"admin_{fake.user_name()}",
        email=fake.email(),
        hashed_password=get_password_hash("adminpassword123"),
        is_verified=True,
        is_superuser=True,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def unverified_user(test_session: AsyncSession) -> User:
    """
    Create an unverified test user.

    Useful for testing email verification flows.
    """
    user = User(
        id=uuid.uuid4(),
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash("testpassword123"),
        is_verified=False,
        is_superuser=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """
    Generate authentication headers for a test user.

    Returns headers dict with Bearer token that can be passed to HTTP requests.
    """
    token = create_access_token(sub=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def superuser_auth_headers(test_superuser: User) -> dict[str, str]:
    """
    Generate authentication headers for a superuser.
    """
    token = create_access_token(sub=str(test_superuser.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> AsyncClient:
    """
    Create an authenticated HTTP client.

    This client includes authentication headers in all requests.
    """
    async_client.headers.update(auth_headers)
    return async_client


# ============================================================================
# Helper Fixtures
# ============================================================================


@pytest.fixture
def faker_instance() -> Faker:
    """
    Provide a Faker instance for generating test data.
    """
    return fake
