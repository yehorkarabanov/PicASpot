import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Index, types
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.area.models import Area
    from app.landmark.models import Landmark
    from app.unlock.models import Unlock


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        default=False, nullable=False, index=True
    )
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)

    # Relationships - back references from foreign keys
    created_areas: Mapped[list["Area"]] = relationship(
        "Area", back_populates="creator", foreign_keys="Area.created_by"
    )
    created_landmarks: Mapped[list["Landmark"]] = relationship(
        "Landmark", back_populates="creator", foreign_keys="Landmark.created_by"
    )
    unlocks: Mapped[list["Unlock"]] = relationship(
        "Unlock", back_populates="user"
    )


# Composite index for email and is_verified for faster queries
Index("idx_user_email_verified", User.email, User.is_verified)
