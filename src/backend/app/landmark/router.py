from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep

from .dependencies import LandmarkServiceDep
from .schemas import LandmarkCreate, LandmarkReturn

router = APIRouter(prefix="/landmark", tags=["landmark"])


@router.post("/", response_model=LandmarkReturn, response_model_exclude_none=True)
async def create_landmark(
    landmark_data: LandmarkCreate,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkReturn:
    """Create a new landmark."""
    landmark_response = await landmark_service.create_landmark(
        landmark_data=landmark_data, creator_id=current_user.id
    )
    return LandmarkReturn(
        message="Landmark created successfully", data=landmark_response
    )
