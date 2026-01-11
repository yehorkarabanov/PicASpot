import datetime
import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, types
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.landmark.models import Landmark
    from app.user.models import User


class AttemptStatus(str, enum.Enum):
    """Status of a landmark unlock attempt"""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    landmark_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("landmarks.id", ondelete="CASCADE"),
        nullable=False,
    )
    photo_url: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(
        types.Enum(AttemptStatus, native_enum=False),
        default=AttemptStatus.PENDING,
        nullable=False,
    )
    similarity_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(nullable=True)

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # lazy="raise" prevents accidental lazy loading in async context
    # Use selectinload() or joinedload() in queries to explicitly load relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="attempts", foreign_keys=[user_id], lazy="raise"
    )
    landmark: Mapped["Landmark"] = relationship(
        "Landmark", back_populates="attempts", foreign_keys=[landmark_id], lazy="raise"
    )
    unlock: Mapped[Optional["Unlock"]] = relationship(
        "Unlock", back_populates="attempt", uselist=False, lazy="raise"
    )

    def __repr__(self) -> str:
        return f"<Attempt(id={self.id}, user_id={self.user_id}, landmark_id={self.landmark_id}, status={self.status})>"


# Attempt composite indexes for common query patterns:
# Get all attempts by a user ordered by time (for user attempt history)
Index("idx_attempt_user_created_at", Attempt.user_id, Attempt.created_at)
# Get all attempts for a landmark ordered by time (for landmark verification queue)
Index("idx_attempt_landmark_created_at", Attempt.landmark_id, Attempt.created_at)
# Get pending attempts by user (check if user has pending attempts)
Index("idx_attempt_user_status", Attempt.user_id, Attempt.status)
# Get pending attempts for a landmark (verification queue for specific landmark)
Index("idx_attempt_landmark_status", Attempt.landmark_id, Attempt.status)
# Get all pending attempts ordered by time (global verification queue)
Index("idx_attempt_status_created_at", Attempt.status, Attempt.created_at)


class Unlock(Base):
    __tablename__ = "unlocks"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    landmark_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("landmarks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid,
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    photo_url: Mapped[str] = mapped_column(nullable=False)
    is_posted_to_feed: Mapped[bool] = mapped_column(default=False, nullable=False)

    unlocked_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    # lazy="raise" prevents accidental lazy loading in async context
    # Use selectinload() or joinedload() in queries to explicitly load relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="unlocks", foreign_keys=[user_id], lazy="raise"
    )
    landmark: Mapped["Landmark"] = relationship(
        "Landmark", back_populates="unlocks", foreign_keys=[landmark_id], lazy="raise"
    )
    attempt: Mapped["Attempt"] = relationship(
        "Attempt", back_populates="unlock", foreign_keys=[attempt_id], lazy="raise"
    )

    def __repr__(self) -> str:
        return (
            f"<Unlock(user_id={self.user_id}, landmark_id={self.landmark_id}, "
            f"unlocked_at={self.unlocked_at})>"
        )


# Pair combinations not covered by PK left-prefix rule:
# Get all unlocks by a user for a specific landmark (check if user unlocked landmark)
Index("idx_unlock_user_landmark", Unlock.user_id, Unlock.landmark_id)

# Time-based queries:
# Get all unlocks by a user ordered by time (for user unlock history)
Index("idx_unlock_user_unlocked_at", Unlock.user_id, Unlock.unlocked_at)
# Get feed posts ordered by time (for social feed feature)
Index("idx_unlock_feed_unlocked_at", Unlock.is_posted_to_feed, Unlock.unlocked_at)
# Get unlocks for a specific landmark ordered by time (for landmark popularity/statistics)
Index("idx_unlock_landmark_unlocked_at", Unlock.landmark_id, Unlock.unlocked_at)
