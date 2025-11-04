from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request

from app.database import SessionDep

from .models import User
from .repository import UserRepository
from .service import UserService


def get_timezone(request: Request) -> ZoneInfo:
    """Extract timezone from request state set by TimeZoneMiddleware."""
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, Depends(get_timezone)]


def get_user_repository(session: SessionDep, timezone: TimeZoneDep) -> UserRepository:
    """Get an instance of UserRepository with timezone support."""
    return UserRepository(session=session, model=User, timezone=timezone)


UserRepDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_user_service(user_repository: UserRepDep, timezone: TimeZoneDep) -> UserService:
    """Get an instance of UserService with timezone support."""
    return UserService(user_repository=user_repository, timezone=timezone)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
