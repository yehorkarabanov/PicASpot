from app.core.repository import BaseRepository
from app.user.models import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations"""

    pass
