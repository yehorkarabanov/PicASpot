import datetime
import uuid

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, Index, types
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Landmark(Base):
    __tablename__ = "landmarks"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("areas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    image_url: Mapped[str] = mapped_column(nullable=False)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=False
    )
    unlock_radius_meters: Mapped[int] = mapped_column(default=100, nullable=False)
    photo_radius_meters: Mapped[int] = mapped_column(default=50, nullable=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )


# Composite indexes for common query patterns
# GIST index for geospatial queries (nearby landmarks)
Index("idx_landmark_location", Landmark.location, postgresql_using="gist")
# Get landmarks in an area
Index("idx_landmark_area_creator", Landmark.area_id, Landmark.created_by)
