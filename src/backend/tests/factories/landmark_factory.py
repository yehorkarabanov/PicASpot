"""
Landmark model factory for test data generation.

This factory creates Landmark model instances with realistic fake data,
including geospatial coordinates.
"""

import random
import uuid

from faker import Faker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.ext.asyncio import AsyncSession

from app.area.models import Area
from app.landmark.models import Landmark
from app.user.models import User

fake = Faker()


class LandmarkFactory:
    """
    Factory for creating Landmark instances in tests.

    This class provides methods to create landmarks with valid geospatial
    data and realistic attributes.
    """

    @staticmethod
    async def create(
        session: AsyncSession,
        creator: User,
        area: Area,
        name: str | None = None,
        description: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        image_url: str | None = None,
        unlock_radius_meters: int = 100,
        photo_radius_meters: int = 50,
        **kwargs,
    ) -> Landmark:
        """
        Create a landmark with the given attributes.

        Args:
            session: Database session
            creator: User who creates the landmark
            area: Area where landmark is located
            name: Landmark name (auto-generated if None)
            description: Landmark description (auto-generated if None)
            latitude: Latitude coordinate (auto-generated if None)
            longitude: Longitude coordinate (auto-generated if None)
            image_url: URL to landmark image (auto-generated if None)
            unlock_radius_meters: Radius for unlocking (default: 100m)
            photo_radius_meters: Radius for photo validation (default: 50m)
            **kwargs: Additional landmark attributes

        Returns:
            Created Landmark instance

        Example:
            landmark = await LandmarkFactory.create(session, user, area)
            landmark = await LandmarkFactory.create(
                session, user, area,
                name="Big Ben",
                latitude=51.5007,
                longitude=-0.1246
            )
        """
        # Generate random coordinates if not provided (London area by default)
        if latitude is None:
            latitude = fake.latitude()
        if longitude is None:
            longitude = fake.longitude()

        # Create PostGIS Point geometry
        point = Point(longitude, latitude)  # Note: PostGIS uses (lon, lat)
        location = from_shape(point, srid=4326)

        landmark_data = {
            "id": uuid.uuid4(),
            "area_id": area.id,
            "creator_id": creator.id,
            "name": name or fake.city(),
            "description": description or fake.text(max_nb_chars=200),
            "location": location,
            "image_url": image_url or fake.image_url(),
            "unlock_radius_meters": unlock_radius_meters,
            "photo_radius_meters": photo_radius_meters,
        }
        landmark_data.update(kwargs)

        landmark = Landmark(**landmark_data)
        session.add(landmark)
        await session.commit()
        await session.refresh(landmark)
        return landmark

    @staticmethod
    async def create_batch(
        session: AsyncSession,
        creator: User,
        area: Area,
        count: int = 5,
        **kwargs,
    ) -> list[Landmark]:
        """
        Create multiple landmarks at once.

        Args:
            session: Database session
            creator: User who creates the landmarks
            area: Area where landmarks are located
            count: Number of landmarks to create
            **kwargs: Common attributes for all landmarks

        Returns:
            List of created Landmark instances
        """
        landmarks = []
        for _ in range(count):
            landmark = await LandmarkFactory.create(session, creator, area, **kwargs)
            landmarks.append(landmark)
        return landmarks

    @staticmethod
    async def create_near_location(
        session: AsyncSession,
        creator: User,
        area: Area,
        latitude: float,
        longitude: float,
        max_distance_meters: int = 1000,
        **kwargs,
    ) -> Landmark:
        """
        Create a landmark near a specific location.

        Useful for testing proximity-based features.

        Args:
            session: Database session
            creator: User who creates the landmark
            area: Area where landmark is located
            latitude: Center latitude
            longitude: Center longitude
            max_distance_meters: Maximum distance from center point
            **kwargs: Additional landmark attributes

        Returns:
            Created Landmark instance
        """
        # Calculate offset in degrees (very rough approximation)
        # 1 degree ≈ 111km at equator
        offset_degrees = max_distance_meters / 111000

        # Random offset within max_distance
        lat_offset = random.uniform(-offset_degrees, offset_degrees)
        lon_offset = random.uniform(-offset_degrees, offset_degrees)

        new_lat = latitude + lat_offset
        new_lon = longitude + lon_offset

        return await LandmarkFactory.create(
            session,
            creator,
            area,
            latitude=new_lat,
            longitude=new_lon,
            **kwargs,
        )

    @staticmethod
    def generate_coordinates(
        lat_min: float = -90.0,
        lat_max: float = 90.0,
        lon_min: float = -180.0,
        lon_max: float = 180.0,
    ) -> tuple[float, float]:
        """
        Generate random coordinates within bounds.

        Args:
            lat_min: Minimum latitude
            lat_max: Maximum latitude
            lon_min: Minimum longitude
            lon_max: Maximum longitude

        Returns:
            Tuple of (latitude, longitude)
        """
        latitude = random.uniform(lat_min, lat_max)
        longitude = random.uniform(lon_min, lon_max)
        return latitude, longitude

    @staticmethod
    def generate_london_coordinates() -> tuple[float, float]:
        """Generate random coordinates within London area."""
        # London bounding box (approximate)
        return LandmarkFactory.generate_coordinates(
            lat_min=51.28,
            lat_max=51.69,
            lon_min=-0.51,
            lon_max=0.33,
        )

    @staticmethod
    def generate_name() -> str:
        """Generate a random landmark name."""
        templates = [
            f"{fake.city()} {random.choice(['Tower', 'Bridge', 'Monument', 'Palace', 'Cathedral'])}",
            f"{fake.first_name()}'s {random.choice(['Statue', 'Memorial', 'Square', 'Park'])}",
            f"The {fake.company()} {random.choice(['Building', 'Center', 'Plaza'])}",
        ]
        return random.choice(templates)


__all__ = ["LandmarkFactory"]
