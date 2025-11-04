import datetime
import uuid
from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import ForeignKey, Index, types
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.area.models import Area
    from app.unlock.models import Unlock
    from app.user.models import User


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
    creator_id: Mapped[uuid.UUID] = mapped_column(
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
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # lazy="raise" prevents accidental lazy loading in async context
    # Use selectinload() or joinedload() in queries to explicitly load relationships
    area: Mapped["Area"] = relationship(
        "Area", back_populates="landmarks", foreign_keys=[area_id], lazy="raise"
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_landmarks",
        foreign_keys=[creator_id],
        lazy="raise",
    )
    unlocks: Mapped[list["Unlock"]] = relationship(
        "Unlock", back_populates="landmark", lazy="raise"
    )

    @property
    def latitude(self) -> float:
        """Extract latitude from the location Geography field."""
        from geoalchemy2.shape import to_shape

        point = to_shape(self.location)
        return point.y

    @property
    def longitude(self) -> float:
        """Extract longitude from the location Geography field."""
        from geoalchemy2.shape import to_shape

        point = to_shape(self.location)
        return point.x


# Composite indexes for common query patterns
# GIST index for geospatial queries (nearby landmarks)
Index("idx_landmark_location", Landmark.location, postgresql_using="gist")
# Get landmarks in an area
Index("idx_landmark_area_creator", Landmark.area_id, Landmark.creator_id)
