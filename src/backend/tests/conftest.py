"""
Pytest configuration and shared fixtures for PicASpot backend tests.

This module provides:
- Database fixtures (in-memory SQLite for fast tests)
- Mock services (Storage, Kafka, Redis)
- User fixtures (regular user, admin user)
- FastAPI test client
- Factory fixtures for creating test data

Note: These tests are designed to run in Docker with mocked external services.
For integration tests that require actual services, use the appropriate Docker compose setup.
"""

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Initialize Faker for generating test data
fake = Faker()


# ============================================================================
# Environment Setup for Testing
# ============================================================================

# Set test environment variables before importing app modules
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("PROJECT_NAME", "PicASpot Test")
os.environ.setdefault("DOMAIN", "localhost")
os.environ.setdefault("BACKEND_DEBUG", "true")
os.environ.setdefault("BACKEND_CORS_ORIGINS", '["http://localhost:3000"]')
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_SECONDS", "3600")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("REDIS_HOST", "localhost")
os.environ.setdefault("REDIS_PORT", "6379")
os.environ.setdefault("REDIS_PASSWORD", "test_redis_password")
os.environ.setdefault("EMAIL_VERIFY_PATH", "http://localhost:3000/verify?token=")
os.environ.setdefault("EMAIL_RESET_PASSWORD_PATH", "http://localhost:3000/reset-password?token=")
os.environ.setdefault("MINIO_ROOT_USER", "minioadmin")
os.environ.setdefault("MINIO_ROOT_PASSWORD", "minioadmin")
os.environ.setdefault("DEFAULT_AREA_IMAGE_URL", "http://localhost/static/img/areas/default.jpg")
os.environ.setdefault("DEFAULT_LANDMARK_IMAGE_URL", "http://localhost/static/img/landmarks/default.jpg")

# Now import app modules after environment is set
from app.auth.security import create_access_token, get_password_hash
from app.database.base import Base
from app.user.models import User

# ============================================================================
# Database Fixtures (In-memory SQLite)
# ============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create an async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


# ============================================================================
# Mock Services
# ============================================================================


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service."""
    mock = AsyncMock()
    mock.upload_file = AsyncMock(
        return_value={
            "object_path": "test/path/image.jpg",
            "public_url": "http://localhost/minio/test/path/image.jpg",
            "original_filename": "image.jpg",
            "size": 1024,
        }
    )
    mock.get_presigned_url = AsyncMock(
        return_value="http://localhost/minio/presigned/test.jpg"
    )
    mock.delete_file = AsyncMock(return_value=True)
    mock.get_public_url = MagicMock(
        return_value="http://localhost/minio/test/path/image.jpg"
    )
    return mock


@pytest.fixture
def mock_kafka_producer():
    """Create a mock Kafka producer."""
    mock = AsyncMock()
    mock.start = AsyncMock()
    mock.stop = AsyncMock()
    mock.send_unlock_verify_message = AsyncMock()
    mock.send_verification_email_message = AsyncMock()
    mock.send_password_reset_message = AsyncMock()
    return mock


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.setex = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=1)
    mock.exists = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    mock.ttl = AsyncMock(return_value=60)
    return mock


# ============================================================================
# User Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a regular test user."""
    user = User(
        id=uuid.uuid4(),
        username=fake.user_name(),
        email=fake.email(),
        hashed_password=get_password_hash("TestPassword123"),
        is_verified=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession) -> User:
    """Create an admin/superuser for testing."""
    user = User(
        id=uuid.uuid4(),
        username=f"admin_{fake.user_name()}",
        email=fake.email(),
        hashed_password=get_password_hash("AdminPassword123"),
        is_verified=True,
        is_superuser=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def unverified_user(db_session: AsyncSession) -> User:
    """Create an unverified user for testing."""
    user = User(
        id=uuid.uuid4(),
        username=f"unverified_{fake.user_name()}",
        email=fake.email(),
        hashed_password=get_password_hash("TestPassword123"),
        is_verified=False,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# ============================================================================
# Authentication Fixtures
# ============================================================================


@pytest.fixture
def user_token(test_user: User) -> str:
    """Create an access token for the regular test user."""
    return create_access_token(subject=str(test_user.id))


@pytest.fixture
def admin_token(test_admin_user: User) -> str:
    """Create an access token for the admin user."""
    return create_access_token(subject=str(test_admin_user.id))


@pytest.fixture
def auth_headers(user_token: str) -> dict[str, str]:
    """Create authorization headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict[str, str]:
    """Create authorization headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# FastAPI Test Client
# ============================================================================


@pytest_asyncio.fixture
async def async_client(
    db_session: AsyncSession,
    mock_storage_service,
    mock_kafka_producer,
    mock_redis_client,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async test client with mocked dependencies.

    This fixture patches all external dependencies (database, storage, kafka, redis)
    to allow isolated testing without external services.
    """
    from app.database.manager import get_async_session
    from app.main import app

    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    # Patch external services
    with patch("app.kafka.kafka_producer", mock_kafka_producer):
        with patch(
            "app.database.redis.get_redis_client",
            AsyncMock(return_value=mock_redis_client),
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test/api",
            ) as client:
                yield client

    app.dependency_overrides.clear()


# ============================================================================
# Data Factory Fixtures
# ============================================================================


class UserFactory:
    """Factory for creating test users."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str = "TestPassword123",
        is_verified: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            id=uuid.uuid4(),
            username=username or fake.user_name(),
            email=email or fake.email(),
            hashed_password=get_password_hash(password),
            is_verified=is_verified,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


@pytest.fixture
def user_factory(db_session: AsyncSession) -> UserFactory:
    """Create a user factory instance."""
    return UserFactory(db_session)


# ============================================================================
# Utility Functions
# ============================================================================


def generate_valid_password() -> str:
    """Generate a valid password that meets requirements."""
    return f"Test{fake.random_uppercase_letter()}{fake.random_number(digits=4)}!"


def generate_invalid_passwords() -> list[tuple[str, str]]:
    """Generate invalid passwords with reasons."""
    return [
        ("short", "Password too short"),
        ("nouppercase123", "Missing uppercase letter"),
        ("NoNumbers", "Missing number"),
        ("", "Empty password"),
    ]


# ============================================================================
# Timezone Fixtures
# ============================================================================


@pytest.fixture
def utc_timezone() -> ZoneInfo:
    """UTC timezone for testing."""
    return ZoneInfo("UTC")


@pytest.fixture
def custom_timezone() -> ZoneInfo:
    """Custom timezone for testing timezone conversion."""
    return ZoneInfo("America/New_York")
