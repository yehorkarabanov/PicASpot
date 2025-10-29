import datetime
import uuid

from sqlalchemy import ForeignKey, Index, types
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Unlock(Base):
    __tablename__ = "unlocks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    area_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, ForeignKey("areas.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )
    landmark_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, ForeignKey("landmarks.id", ondelete="CASCADE"), primary_key=True, nullable=False
    )

    photo_url: Mapped[str] = mapped_column(nullable=False)
    posted_to_feed: Mapped[bool] = mapped_column(default=False, nullable=False)

    unlocked_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

# Pair combinations not covered by PK left-prefix rule:
# Get all unlocks in an area for a specific landmark (area completion tracking)
Index('idx_unlock_area_landmark', Unlock.area_id, Unlock.landmark_id)
# Get all unlocks by a user for a specific landmark (check if user unlocked landmark)
Index('idx_unlock_user_landmark', Unlock.user_id, Unlock.landmark_id)

# Time-based queries:
# Get all unlocks by a user ordered by time (for user unlock history)
Index('idx_unlock_user_unlocked_at', Unlock.user_id, Unlock.unlocked_at)
# Get feed posts ordered by time (for social feed feature)
Index('idx_unlock_feed_unlocked_at', Unlock.posted_to_feed, Unlock.unlocked_at)
# Get unlocks for a specific area ordered by time (for area statistics/leaderboards)
Index('idx_unlock_area_unlocked_at', Unlock.area_id, Unlock.unlocked_at)
# Get unlocks for a specific landmark ordered by time (for landmark popularity/statistics)
Index('idx_unlock_landmark_unlocked_at', Unlock.landmark_id, Unlock.unlocked_at)

