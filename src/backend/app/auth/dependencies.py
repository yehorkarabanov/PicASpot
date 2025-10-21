from .models import User
from .repository import UserRepository
from ..database import SessionDep


# Repository
def get_user_repository(session: SessionDep) -> UserRepository:
    """Get an instance of UserRepository."""
    return UserRepository(session=session, model=User)

