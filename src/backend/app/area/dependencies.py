from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends, Request

from app.database import SessionDep
from app.storage import StorageServiceDep

from .models import Area
from .repository import AreaRepository
from .service import AreaService


def get_timezone(request: Request) -> ZoneInfo:
    """Extract timezone from request state set by TimeZoneMiddleware."""
    return getattr(request.state, "timezone", ZoneInfo("UTC"))


TimeZoneDep = Annotated[ZoneInfo, Depends(get_timezone)]


def get_area_repository(session: SessionDep, timezone: TimeZoneDep) -> AreaRepository:
    """Get an instance of AreaRepository with timezone support."""
    return AreaRepository(session=session, model=Area, timezone=timezone)


AreaRepDep = Annotated[AreaRepository, Depends(get_area_repository)]


def get_area_service(
    area_repository: AreaRepDep,
    storage: StorageServiceDep,
    timezone: TimeZoneDep,
) -> AreaService:
    """Get an instance of AreaService with timezone support."""
    return AreaService(
        area_repository=area_repository, storage=storage, timezone=timezone
    )


AreaServiceDep = Annotated[AreaService, Depends(get_area_service)]
