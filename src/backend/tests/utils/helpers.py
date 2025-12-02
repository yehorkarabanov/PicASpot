"""
Test helper functions.

This module provides utility functions for common testing tasks,
such as creating test users, generating tokens, and working with
geospatial data.
"""

import uuid
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, get_password_hash
from app.user.models import User

fake = Faker()


async def create_test_user(
    session: AsyncSession,
    username: str | None = None,
    email: str | None = None,
    password: str = "testpassword123",
    is_verified: bool = True,
    is_superuser: bool = False,
) -> User:
    """
    Create a test user with given attributes.

    This is a convenience function for quickly creating users in tests.
    For more advanced use cases, prefer using UserFactory.

    Args:
        session: Database session
        username: Username (auto-generated if None)
        email: Email address (auto-generated if None)
        password: Plain text password (will be hashed)
        is_verified: Email verification status
        is_superuser: Superuser/admin status

    Returns:
        Created User instance

    Example:
        user = await create_test_user(session)
        admin = await create_test_user(session, is_superuser=True)
    """
    user = User(
        id=uuid.uuid4(),
        username=username or fake.user_name(),
        email=email or fake.email(),
        hashed_password=get_password_hash(password),
        is_verified=is_verified,
        is_superuser=is_superuser,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


def generate_token(user_id: str | uuid.UUID, **extra_data) -> str:
    """
    Generate a JWT authentication token for a user.

    Args:
        user_id: User ID to encode in token
        **extra_data: Additional claims to include in token

    Returns:
        JWT token string

    Example:
        token = generate_token(user.id)
        headers = {"Authorization": f"Bearer {token}"}
    """
    return create_access_token(sub=str(user_id), extra_data=extra_data)


def create_auth_headers(user_id: str | uuid.UUID) -> dict[str, str]:
    """
    Create authentication headers for API requests.

    Args:
        user_id: User ID to authenticate as

    Returns:
        Dictionary with Authorization header

    Example:
        headers = create_auth_headers(user.id)
        response = await client.get("/api/v1/users/me", headers=headers)
    """
    token = generate_token(user_id)
    return {"Authorization": f"Bearer {token}"}


def create_geojson_point(latitude: float, longitude: float) -> dict:
    """
    Create a valid GeoJSON Point geometry.

    Note: GeoJSON uses [longitude, latitude] order (opposite of intuition).

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)

    Returns:
        GeoJSON Point dictionary

    Example:
        point = create_geojson_point(51.5074, -0.1278)
        # Returns: {"type": "Point", "coordinates": [-0.1278, 51.5074]}
    """
    return {
        "type": "Point",
        "coordinates": [longitude, latitude],  # GeoJSON is [lon, lat]
    }


def create_geojson_polygon(coordinates: list[list[list[float]]]) -> dict:
    """
    Create a valid GeoJSON Polygon geometry.

    Args:
        coordinates: List of linear rings (first is exterior, rest are holes)
                    Each ring is a list of [lon, lat] coordinates
                    First and last coordinate must be identical (closed ring)

    Returns:
        GeoJSON Polygon dictionary

    Example:
        # Simple rectangle
        polygon = create_geojson_polygon([[
            [-0.1, 51.5],
            [-0.1, 51.6],
            [-0.2, 51.6],
            [-0.2, 51.5],
            [-0.1, 51.5]  # Close the ring
        ]])
    """
    return {
        "type": "Polygon",
        "coordinates": coordinates,
    }


def create_simple_polygon(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
) -> dict:
    """
    Create a simple rectangular GeoJSON polygon.

    Args:
        min_lat: Minimum latitude
        max_lat: Maximum latitude
        min_lon: Minimum longitude
        max_lon: Maximum longitude

    Returns:
        GeoJSON Polygon dictionary

    Example:
        # London bounding box
        polygon = create_simple_polygon(51.28, 51.69, -0.51, 0.33)
    """
    return create_geojson_polygon(
        [
            [
                [min_lon, min_lat],
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat],
                [min_lon, min_lat],  # Close the ring
            ]
        ]
    )


def assert_datetime_equal(
    dt1: datetime,
    dt2: datetime,
    tolerance_seconds: int = 2,
) -> bool:
    """
    Compare two datetime objects with a tolerance.

    This is useful for comparing database timestamps that might have
    slight differences due to rounding or processing time.

    Args:
        dt1: First datetime
        dt2: Second datetime
        tolerance_seconds: Maximum allowed difference in seconds

    Returns:
        True if datetimes are within tolerance

    Example:
        assert assert_datetime_equal(user.created_at, datetime.now(timezone.utc))
    """
    # Ensure both are timezone-aware
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=timezone.utc)

    diff = abs((dt1 - dt2).total_seconds())
    return diff <= tolerance_seconds


def normalize_datetime(dt: datetime) -> datetime:
    """
    Normalize datetime to UTC timezone.

    Args:
        dt: Datetime to normalize

    Returns:
        Datetime in UTC timezone

    Example:
        utc_dt = normalize_datetime(local_dt)
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def generate_random_coordinates(
    center_lat: float = 51.5074,
    center_lon: float = -0.1278,
    radius_km: float = 10.0,
) -> tuple[float, float]:
    """
    Generate random coordinates near a center point.

    Args:
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Maximum distance from center in kilometers

    Returns:
        Tuple of (latitude, longitude)

    Example:
        lat, lon = generate_random_coordinates()  # Near London
    """
    import random

    # Rough approximation: 1 degree ≈ 111km
    offset_degrees = radius_km / 111.0

    lat_offset = random.uniform(-offset_degrees, offset_degrees)
    lon_offset = random.uniform(-offset_degrees, offset_degrees)

    return center_lat + lat_offset, center_lon + lon_offset


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate that coordinates are within valid ranges.

    Args:
        latitude: Latitude to validate
        longitude: Longitude to validate

    Returns:
        True if coordinates are valid

    Example:
        assert validate_coordinates(51.5074, -0.1278)
    """
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_geojson_point(geojson: dict) -> bool:
    """
    Validate GeoJSON Point structure.

    Args:
        geojson: GeoJSON object to validate

    Returns:
        True if valid GeoJSON Point

    Example:
        point = {"type": "Point", "coordinates": [-0.1278, 51.5074]}
        assert validate_geojson_point(point)
    """
    if not isinstance(geojson, dict):
        return False

    if geojson.get("type") != "Point":
        return False

    coords = geojson.get("coordinates")
    if not isinstance(coords, list) or len(coords) != 2:
        return False

    lon, lat = coords
    return validate_coordinates(lat, lon)


__all__ = [
    "create_test_user",
    "generate_token",
    "create_auth_headers",
    "create_geojson_point",
    "create_geojson_polygon",
    "create_simple_polygon",
    "assert_datetime_equal",
    "normalize_datetime",
    "generate_random_coordinates",
    "validate_coordinates",
    "validate_geojson_point",
]
