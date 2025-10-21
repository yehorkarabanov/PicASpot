from typing import Annotated

from fastapi import Depends

from app.database import SessionDep

from .models import User
from .repository import UserRepository
from .service import UserService


def get_user_repository(session: SessionDep) -> UserRepository:
    """Get an instance of UserRepository."""
    return UserRepository(session=session, model=User)


UserRepDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_user_service(user_repository: UserRepDep) -> UserService:
    """Get an instance of UserService."""
    return UserService(user_repository=user_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
