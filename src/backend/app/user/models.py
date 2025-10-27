import uuid

from sqlalchemy import Index, types
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        types.Uuid, primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False, index=True)


# Composite index for email and is_verified for faster queries
Index('idx_user_email_verified', User.email, User.is_verified)
