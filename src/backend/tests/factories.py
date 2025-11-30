"""
Factory functions for generating test data using Faker.

This module provides factory functions to create test instances
of various models with realistic fake data.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from faker import Faker
from geoalchemy2 import WKTElement

from app.auth.security import get_password_hash

fake = Faker()


def user_factory(**kwargs: Any) -> Dict[str, Any]:
    """
    Create user test data.

    Args:
        **kwargs: Override default values for specific fields.

    Returns:
        Dictionary of user data suitable for User model creation.
    """
    defaults = {
        "id": uuid.uuid4(),
        "username": fake.user_name(),
        "email": fake.email(),
        "hashed_password": get_password_hash("TestPassword123!"),
        "is_verified": True,
        "is_superuser": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return defaults


def area_factory(**kwargs: Any) -> Dict[str, Any]:
    """
    Create area test data.

    Args:
        **kwargs: Override default values for specific fields.

    Returns:
        Dictionary of area data suitable for Area model creation.
    """
    defaults = {
        "id": uuid.uuid4(),
        "name": fake.city(),
        "description": fake.text(max_nb_chars=200),
        "parent_area_id": None,
        "creator_id": uuid.uuid4(),
        "is_verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return defaults


def landmark_factory(**kwargs: Any) -> Dict[str, Any]:
    """
    Create landmark test data with geospatial coordinates.

    Args:
        **kwargs: Override default values for specific fields.

    Returns:
        Dictionary of landmark data suitable for Landmark model creation.
    """
    # Generate random coordinates (latitude, longitude)
    lat = float(fake.latitude())
    lon = float(fake.longitude())

    defaults = {
        "id": uuid.uuid4(),
        "name": fake.street_name(),
        "description": fake.text(max_nb_chars=200),
        "location": f"POINT({lon} {lat})",  # WKT format for PostGIS
        "area_id": uuid.uuid4(),
        "creator_id": uuid.uuid4(),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return defaults


def unlock_factory(**kwargs: Any) -> Dict[str, Any]:
    """
    Create unlock test data.

    Args:
        **kwargs: Override default values for specific fields.

    Returns:
        Dictionary of unlock data suitable for Unlock model creation.
    """
    defaults = {
        "user_id": uuid.uuid4(),
        "area_id": uuid.uuid4(),
        "landmark_id": uuid.uuid4(),
        "is_posted_to_feed": False,
        "unlocked_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return defaults


def create_coordinates(lat: float = None, lon: float = None) -> str:
    """
    Create WKT POINT string for geospatial data.

    Args:
        lat: Latitude (default: random)
        lon: Longitude (default: random)

    Returns:
        WKT POINT string.
    """
    if lat is None:
        lat = float(fake.latitude())
    if lon is None:
        lon = float(fake.longitude())
    return f"POINT({lon} {lat})"


def create_nearby_coordinates(
    base_lat: float, base_lon: float, max_distance_km: float = 1.0
) -> str:
    """
    Create coordinates near a base point.

    Args:
        base_lat: Base latitude
        base_lon: Base longitude
        max_distance_km: Maximum distance in kilometers

    Returns:
        WKT POINT string for nearby coordinates.
    """
    # Approximate: 1 degree ≈ 111 km
    offset = max_distance_km / 111.0
    lat = base_lat + fake.pyfloat(min_value=-offset, max_value=offset)
    lon = base_lon + fake.pyfloat(min_value=-offset, max_value=offset)
    return f"POINT({lon} {lat})"

