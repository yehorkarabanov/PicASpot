from typing import Annotated

from fastapi import Depends

from app.database import SessionDep

from .models import Area
from .repository import AreaRepository
from .service import AreaService


def get_area_repository(session: SessionDep) -> AreaRepository:
    """Get an instance of AreaRepository."""
    return AreaRepository(session=session, model=Area)


AreaRepDep = Annotated[AreaRepository, Depends(get_area_repository)]


def get_area_service(area_repository: AreaRepDep) -> AreaService:
    """Get an instance of AreaService."""
    return AreaService(area_repository=area_repository)


AreaServiceDep = Annotated[AreaService, Depends(get_area_service)]
