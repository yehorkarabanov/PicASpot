from .models import User

from app.core.repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations"""

    pass