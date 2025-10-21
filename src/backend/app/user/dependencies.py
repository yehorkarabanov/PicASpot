from typing import Annotated

from fastapi import Depends

from app.database import SessionDep
from app.user.repository import UserRepository

from .models import User


def get_user_repository(session: SessionDep) -> UserRepository:
    """Get an instance of UserRepository."""
    return UserRepository(session=session, model=User)  # noqa: F821


UserRepDep = Annotated[UserRepository, Depends(get_user_repository)]