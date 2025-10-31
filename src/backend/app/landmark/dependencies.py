from typing import Annotated

from fastapi import Depends

from app.area.dependencies import AreaRepDep
from app.database import SessionDep

from .models import Landmark
from .repository import LandmarkRepository
from .service import LandmarkService


def get_landmark_repository(session: SessionDep) -> LandmarkRepository:
    """Get an instance of LandmarkRepository."""
    return LandmarkRepository(session=session, model=Landmark)


LandmarkRepDep = Annotated[LandmarkRepository, Depends(get_landmark_repository)]


def get_landmark_service(
    landmark_repository: LandmarkRepDep, area_repository: AreaRepDep
) -> LandmarkService:
    """Get an instance of LandmarkService."""
    return LandmarkService(
        landmark_repository=landmark_repository, area_repository=area_repository
    )


LandmarkServiceDep = Annotated[LandmarkService, Depends(get_landmark_service)]
