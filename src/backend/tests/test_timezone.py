"""
Integration test for timezone functionality.

Run this test to verify that timezone conversion is working correctly
across all repositories and the middleware.
"""

import uuid
from zoneinfo import ZoneInfo

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import convert_utc_to_timezone, get_utc_now
from app.main import app
from app.user.models import User
from app.user.repository import UserRepository


@pytest.mark.asyncio
async def test_timezone_utils():
    """Test timezone utility functions"""
    # Test get_utc_now
    utc_now = get_utc_now()
    assert utc_now.tzinfo.key == "UTC"

    # Test conversion to different timezones
    ny_time = convert_utc_to_timezone(utc_now, ZoneInfo("America/New_York"))
    assert ny_time.tzinfo.key == "America/New_York"

    london_time = convert_utc_to_timezone(utc_now, ZoneInfo("Europe/London"))
    assert london_time.tzinfo.key == "Europe/London"

    # Verify they represent the same instant
    assert utc_now.timestamp() == ny_time.timestamp()
    assert utc_now.timestamp() == london_time.timestamp()


@pytest.mark.asyncio
async def test_repository_timezone_conversion(db_session: AsyncSession):
    """Test that repository converts timestamps based on timezone"""
    # Create a user
    user_data = {
        "id": uuid.uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed",
        "is_superuser": False,
        "is_verified": True,
    }

    # Repository with UTC timezone
    utc_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("UTC"))
    user_utc = await utc_repo.create(user_data)

    # Repository with New York timezone
    ny_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("America/New_York"))
    user_ny = await ny_repo.get_by_id(user_utc.id)

    # Repository with London timezone
    london_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("Europe/London"))
    user_london = await london_repo.get_by_id(user_utc.id)

    # Verify timestamps are in different timezones but represent same instant
    assert user_utc.created_at.tzinfo.key == "UTC"
    assert user_ny.created_at.tzinfo.key == "America/New_York"
    assert user_london.created_at.tzinfo.key == "Europe/London"

    # All should represent the same moment in time
    assert user_utc.created_at.timestamp() == user_ny.created_at.timestamp()
    assert user_utc.created_at.timestamp() == user_london.created_at.timestamp()


@pytest.mark.asyncio
async def test_timezone_middleware():
    """Test that middleware extracts timezone from header"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request with timezone header
        response = await client.get(
            "/v1/examples/timezone-info",
            headers={"X-Timezone": "America/New_York"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "America/New_York"

        # Request without timezone header (should default to UTC)
        response = await client.get("/v1/examples/timezone-info")
        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "UTC"

        # Request with invalid timezone (should default to UTC)
        response = await client.get(
            "/v1/examples/timezone-info",
            headers={"X-Timezone": "Invalid/Timezone"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "UTC"


@pytest.mark.asyncio
async def test_repository_get_all_with_timezone(db_session: AsyncSession):
    """Test that get_all converts all entities' timestamps"""
    # Create multiple users
    for i in range(3):
        user_data = {
            "id": uuid.uuid4(),
            "username": f"testuser{i}",
            "email": f"test{i}@example.com",
            "hashed_password": "hashed",
            "is_superuser": False,
            "is_verified": True,
        }
        repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("UTC"))
        await repo.create(user_data)

    # Get all users with Tokyo timezone
    tokyo_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("Asia/Tokyo"))
    users = await tokyo_repo.get_all()

    # Verify all users have timestamps in Tokyo timezone
    for user in users:
        assert user.created_at.tzinfo.key == "Asia/Tokyo"
        assert user.updated_at.tzinfo.key == "Asia/Tokyo"


@pytest.mark.asyncio
async def test_repository_update_with_timezone(db_session: AsyncSession):
    """Test that update converts timestamps"""
    # Create a user
    user_data = {
        "id": uuid.uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed",
        "is_superuser": False,
        "is_verified": True,
    }

    repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("UTC"))
    user = await repo.create(user_data)

    # Update with Sydney timezone
    sydney_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("Australia/Sydney"))
    updated_user = await sydney_repo.update(user.id, {"username": "updated_user"})

    # Verify timestamps are in Sydney timezone
    assert updated_user.created_at.tzinfo.key == "Australia/Sydney"
    assert updated_user.updated_at.tzinfo.key == "Australia/Sydney"


@pytest.mark.asyncio
async def test_custom_repository_methods(db_session: AsyncSession):
    """Test that custom repository methods also convert timestamps"""
    # Create a user
    user_data = {
        "id": uuid.uuid4(),
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": "hashed",
        "is_superuser": False,
        "is_verified": True,
    }

    repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("UTC"))
    await repo.create(user_data)

    # Use custom method with Paris timezone
    paris_repo = UserRepository(session=db_session, model=User, timezone=ZoneInfo("Europe/Paris"))
    user = await paris_repo.get_by_email_or_username("test@example.com", "testuser")

    # Verify timestamps are in Paris timezone
    assert user.created_at.tzinfo.key == "Europe/Paris"
    assert user.updated_at.tzinfo.key == "Europe/Paris"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

