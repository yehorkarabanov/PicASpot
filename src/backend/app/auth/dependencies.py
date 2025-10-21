from fastapi import Depends

from .models import User
from .repository import UserRepository
from .service import AuthService
from ..database import SessionDep


# Repository
def get_user_repository(session: SessionDep) -> UserRepository:
    """Get an instance of UserRepository."""
    return UserRepository(session=session, model=User)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository=user_repository)