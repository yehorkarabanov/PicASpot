"""
Database-related test fixtures.

This module provides fixtures for database engine, sessions,
and database cleanup utilities.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database.base import Base
from app.settings import settings


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create a test database engine for the entire test session.

    The test database is created at the start of the test session
    and destroyed at the end. All tests share this engine.
    """
    # Create test database URL
    test_db_url = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}_test"

    # Create engine with test-optimized settings
    engine = create_async_engine(
        url=test_db_url,
        echo=False,  # Disable SQL logging in tests for cleaner output
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # Create all tables at session start
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup: Drop all tables and dispose engine at session end
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def test_session_maker(
    test_engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """
    Create a session factory for tests.

    This factory creates isolated database sessions for each test,
    ensuring test independence.
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

    Each test gets its own isolated session. All changes are rolled back
    after the test completes, ensuring complete test isolation.
    """
    async with test_session_maker() as session:
        async with session.begin():
            yield session
            # Automatic rollback ensures test isolation
            await session.rollback()


@pytest_asyncio.fixture
async def clean_database(test_session: AsyncSession) -> AsyncGenerator[None, None]:
    """
    Ensure database is clean between tests.

    This fixture truncates all tables after each test to prevent
    data leakage between tests. Use this when you need a completely
    clean slate for each test.
    """
    yield

    # Cleanup after test - delete all data
    await test_session.rollback()

    async with test_session.begin():
        # Delete in reverse order of foreign key dependencies
        await test_session.execute(text("TRUNCATE TABLE unlocks CASCADE"))
        await test_session.execute(text("TRUNCATE TABLE landmarks CASCADE"))
        await test_session.execute(text("TRUNCATE TABLE areas CASCADE"))
        await test_session.execute(text("TRUNCATE TABLE users CASCADE"))
        await test_session.commit()


__all__ = ["test_engine", "test_session_maker", "test_session", "clean_database"]
