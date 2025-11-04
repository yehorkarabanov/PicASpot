from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request

from app.area.dependencies import AreaRepDep
from app.database import SessionDep

from .models import Landmark
from .repository import LandmarkRepository
from .service import LandmarkService


def get_timezone(request: Request) -> ZoneInfo:
    """Extract timezone from request state set by TimeZoneMiddleware."""
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, Depends(get_timezone)]


def get_landmark_repository(
    session: SessionDep, timezone: TimeZoneDep
) -> LandmarkRepository:
    """Get an instance of LandmarkRepository with timezone support."""
    return LandmarkRepository(session=session, model=Landmark, timezone=timezone)


LandmarkRepDep = Annotated[LandmarkRepository, Depends(get_landmark_repository)]


def get_landmark_service(
    landmark_repository: LandmarkRepDep, area_repository: AreaRepDep
) -> LandmarkService:
    """Get an instance of LandmarkService."""
    return LandmarkService(
        landmark_repository=landmark_repository, area_repository=area_repository
    )


LandmarkServiceDep = Annotated[LandmarkService, Depends(get_landmark_service)]
