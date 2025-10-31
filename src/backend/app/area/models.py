import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, types
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.landmark.models import Landmark
    from app.unlock.models import Unlock
    from app.user.models import User


class Area(Base):
    __tablename__ = "areas"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    parent_area_id: Mapped[uuid.UUID | None] = mapped_column(
        types.Uuid,
        ForeignKey("areas.id", ondelete="CASCADE"),
        nullable=True,
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
    image_url: Mapped[str | None] = mapped_column(nullable=True)
    badge_url: Mapped[str | None] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_areas", foreign_keys=[created_by]
    )
    parent_area: Mapped["Area | None"] = relationship(
        "Area", remote_side=[id], back_populates="child_areas", foreign_keys=[parent_area_id]
    )
    child_areas: Mapped[list["Area"]] = relationship(
        "Area", back_populates="parent_area", foreign_keys=[parent_area_id]
    )
    landmarks: Mapped[list["Landmark"]] = relationship(
        "Landmark", back_populates="area"
    )
    unlocks: Mapped[list["Unlock"]] = relationship(
        "Unlock", back_populates="area"
    )


# Composite indexes for common query patterns
# Get verified child areas of a parent
Index("idx_area_parent_verified", Area.parent_area_id, Area.is_verified)
# Get verified areas created by a user
Index("idx_area_creator_verified", Area.created_by, Area.is_verified)
