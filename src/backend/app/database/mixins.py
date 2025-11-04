"""Database model mixins for common functionality."""

import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp fields to models.

    These fields are automatically managed by the database:
    - created_at: Set to current UTC time on record creation
    - updated_at: Set to current UTC time on record creation and updated on every modification

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            # created_at and updated_at are inherited from TimestampMixin
    """

    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False, index=True
    )
