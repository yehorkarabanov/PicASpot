from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.settings import settings

from .base import Base

# Engine with proper pooling
engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL logging in debug mode
    # Connection pool settings (defaults are good, but here's explicit config):
    pool_size=5,  # Min connections kept alive
    max_overflow=10,  # Max extra connections during load spikes
    pool_pre_ping=True,  # Check connection health before use (prevents "gone away" errors)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
)

# Session factory
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit (better for APIs)
    autoflush=False,  # Manual control over flushes (more predictable)
    autocommit=False,  # Always explicit commits (safer)
)


# Dependency for FastAPI
async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
        # Automatic cleanup:
        # - Commits if no exception
        # - Rolls back if exception
        # - Closes connection and returns it to pool


# Create tables (call once at startup)
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Optional: Dispose engine on shutdown
async def dispose_engine():
    await engine.dispose()
