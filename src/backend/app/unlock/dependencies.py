from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request

from app.database import SessionDep
from app.landmark.dependencies import LandmarkRepDep
from app.storage.dependencies import StorageServiceDep

from .models import Unlock
from .repository import UnlockRepository
from .service import UnlockService


def get_timezone(request: Request) -> ZoneInfo:
    """Extract timezone from request state set by TimeZoneMiddleware."""
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, Depends(get_timezone)]


def get_unlock_repository(
    session: SessionDep, timezone: TimeZoneDep
) -> UnlockRepository:
    """Get an instance of UnlockRepository with timezone support."""
    return UnlockRepository(session=session, model=Unlock, timezone=timezone)


UnlockRepDep = Annotated[UnlockRepository, Depends(get_unlock_repository)]


def get_unlock_service(
    unlock_repository: UnlockRepDep,
    landmark_repository: LandmarkRepDep,
    storage: StorageServiceDep,
    timezone: TimeZoneDep,
) -> UnlockService:
    """Get an instance of UnlockService."""
    return UnlockService(
        unlock_repository=unlock_repository,
        landmark_repository=landmark_repository,
        storage=storage,
        timezone=timezone,
    )


UnlockServiceDep = Annotated[UnlockService, Depends(get_unlock_service)]
