from typing import Annotated

from fastapi import Depends

from app.database import SessionDep
from app.landmark.models import Landmark
from app.landmark.repository import LandmarkRepository
from app.landmark.service import LandmarkService


def get_landmark_repository(session: SessionDep) -> LandmarkRepository:
    """Get an instance of LandmarkRepository."""
    return LandmarkRepository(session=session, model=Landmark)


LandmarkRepDep = Annotated[LandmarkRepository, Depends(get_landmark_repository)]


def get_landmark_service(landmark_repository: LandmarkRepDep) -> LandmarkService:
    """Get an instance of LandmarkService."""
    return LandmarkService(landmark_repository=landmark_repository)


LandmarkServiceDep = Annotated[LandmarkService, Depends(get_landmark_service)]
