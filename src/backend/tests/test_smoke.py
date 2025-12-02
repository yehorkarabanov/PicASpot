"""
Smoke tests to verify test infrastructure is working correctly.

These tests validate that fixtures, factories, and utilities are
properly configured before running the full test suite.
"""

from datetime import datetime, timezone

import pytest


@pytest.mark.unit
class TestTestInfrastructure:
    """Verify test infrastructure is working."""

    def test_pytest_working(self):
        """Verify pytest is running correctly."""
        assert True

    def test_faker_available(self, faker_instance):
        """Verify Faker is configured and accessible."""
        from faker import Faker

        assert faker_instance is not None
        assert isinstance(faker_instance, Faker)

        # Generate some fake data
        name = faker_instance.name()
        email = faker_instance.email()

        assert isinstance(name, str)
        assert isinstance(email, str)
        assert "@" in email

    @pytest.mark.asyncio
    async def test_async_tests_working(self):
        """Verify async tests can run."""
        import asyncio

        result = await asyncio.sleep(0, result="async_works")
        assert result == "async_works"


@pytest.mark.integration
class TestDatabaseFixtures:
    """Verify database fixtures are working."""

    @pytest.mark.asyncio
    async def test_database_session(self, test_session):
        """Verify database session fixture works."""
        from sqlalchemy.ext.asyncio import AsyncSession

        assert test_session is not None
        assert isinstance(test_session, AsyncSession)

    @pytest.mark.asyncio
    async def test_clean_database_fixture(self, test_session, clean_database):
        """Verify clean_database fixture works."""
        from sqlalchemy import text

        # Should be able to query the database
        result = await test_session.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        assert row[0] == 1


@pytest.mark.integration
class TestFactories:
    """Verify factory classes are working."""

    @pytest.mark.asyncio
    async def test_user_factory(self, test_session, clean_database):
        """Verify UserFactory creates users correctly."""
        from tests.factories import UserFactory

        user = await UserFactory.create(test_session, username="testuser")

        assert user is not None
        assert user.id is not None
        assert user.username == "testuser"
        assert user.hashed_password is not None

    @pytest.mark.asyncio
    async def test_area_factory(self, test_session, clean_database):
        """Verify AreaFactory creates areas correctly."""
        from tests.factories import AreaFactory, UserFactory

        user = await UserFactory.create(test_session)
        area = await AreaFactory.create(test_session, creator=user, name="Test Area")

        assert area is not None
        assert area.id is not None
        assert area.name == "Test Area"
        assert area.creator_id == user.id

    @pytest.mark.asyncio
    async def test_landmark_factory(self, test_session, clean_database):
        """Verify LandmarkFactory creates landmarks correctly."""
        from tests.factories import AreaFactory, LandmarkFactory, UserFactory

        user = await UserFactory.create(test_session)
        area = await AreaFactory.create(test_session, creator=user)
        landmark = await LandmarkFactory.create(
            test_session,
            creator=user,
            area=area,
            name="Test Landmark",
        )

        assert landmark is not None
        assert landmark.id is not None
        assert landmark.name == "Test Landmark"
        assert landmark.creator_id == user.id
        assert landmark.area_id == area.id


@pytest.mark.integration
class TestHTTPClientFixtures:
    """Verify HTTP client fixtures are working."""

    @pytest.mark.asyncio
    async def test_async_client_fixture(self, async_client):
        """Verify async_client fixture works."""
        from httpx import AsyncClient

        assert async_client is not None
        assert isinstance(async_client, AsyncClient)


@pytest.mark.integration
class TestUtilities:
    """Verify test utilities are working."""

    def test_geojson_helpers(self):
        """Verify GeoJSON helper functions work."""
        from tests.utils.helpers import (
            create_geojson_point,
            validate_geojson_point,
        )

        point = create_geojson_point(51.5074, -0.1278)

        assert point["type"] == "Point"
        assert point["coordinates"] == [-0.1278, 51.5074]
        assert validate_geojson_point(point) is True

    def test_custom_assertions(self):
        """Verify custom assertions work."""
        import uuid

        from tests.utils.assertions import (
            assert_has_keys,
            assert_valid_uuid,
        )

        # Test UUID validation
        valid_uuid = str(uuid.uuid4())
        assert_valid_uuid(valid_uuid)

        # Test key validation
        data = {"id": 1, "name": "test", "email": "test@example.com"}
        assert_has_keys(data, ["id", "name", "email"])

    def test_datetime_helpers(self):
        """Verify datetime helper functions work."""
        from tests.utils.helpers import assert_datetime_equal, normalize_datetime

        now = datetime.now(timezone.utc)

        # Same datetime should be equal
        assert assert_datetime_equal(now, now) is True

        # Normalize datetime
        normalized = normalize_datetime(now)
        assert normalized.tzinfo is not None


# Run smoke tests with: pytest tests/test_smoke.py -v
# This verifies the test infrastructure before running full test suite
