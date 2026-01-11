from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request

from app.database import SessionDep
from app.landmark.dependencies import LandmarkRepDep
from app.storage.dependencies import StorageServiceDep

from .models import Attempt, Unlock
from .repository import AttemptRepository, UnlockRepository
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

def get_attempt_repository(
    session: SessionDep, timezone: TimeZoneDep
) -> AttemptRepository:
    """Get an instance of AttemptRepository with timezone support."""
    return AttemptRepository(session=session, model=Attempt, timezone=timezone)

AttemptRepDep = Annotated[AttemptRepository, Depends(get_attempt_repository)]

def get_unlock_service(
    unlock_repository: UnlockRepDep,
    attempt_repository: AttemptRepDep,
    landmark_repository: LandmarkRepDep,
    storage: StorageServiceDep,
    timezone: TimeZoneDep,
) -> UnlockService:
    """Get an instance of UnlockService."""
    return UnlockService(
        unlock_repository=unlock_repository,
        attempt_repository=attempt_repository,
        landmark_repository=landmark_repository,
        storage=storage,
        timezone=timezone,
    )


UnlockServiceDep = Annotated[UnlockService, Depends(get_unlock_service)]
