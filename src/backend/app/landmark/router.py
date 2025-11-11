import uuid

from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep

from .dependencies import LandmarkServiceDep
from .schemas import (
    LandmarkCreate,
    LandmarkListReturn,
    LandmarkNearbyRequest,
    LandmarkReturn,
    LandmarkUpdate,
)

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


@router.get(
    "/{landmark_id}", response_model=LandmarkReturn, response_model_exclude_none=True
)
async def get_landmark(
    landmark_id: uuid.UUID,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkReturn:
    """Get landmark by ID."""
    landmark_response = await landmark_service.get_landmark(landmark_id=landmark_id)
    return LandmarkReturn(
        message="Landmark retrieved successfully", data=landmark_response
    )


@router.delete(
    "/{landmark_id}",
    response_model=LandmarkReturn,
    response_model_exclude_none=True,
)
async def delete_landmark(
    landmark_id: uuid.UUID,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkReturn:
    """Delete landmark by ID."""
    await landmark_service.delete_landmark(landmark_id=landmark_id, user=current_user)
    return LandmarkReturn(message="Landmark deleted successfully")


@router.patch(
    "/{landmark_id}", response_model=LandmarkReturn, response_model_exclude_none=True
)
async def update_landmark(
    landmark_id: uuid.UUID,
    landmark_data: LandmarkUpdate,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkReturn:
    """Update landmark by ID."""
    landmark_response = await landmark_service.update_landmark(
        landmark_id=landmark_id, landmark_data=landmark_data, user=current_user
    )
    return LandmarkReturn(
        message="Landmark updated successfully", data=landmark_response
    )


@router.get(
    "/nearby", response_model=LandmarkListReturn, response_model_exclude_none=True
)
async def get_nearby_landmarks(
    request_data: LandmarkNearbyRequest,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkListReturn:
    """[WIP] Get nearby landmarks based on coordinates and optional filters."""
    return None


@router.get("/nearby-area")
async def get_nearby_landmarks_grouped_by_area(
    request_data: LandmarkNearbyRequest,
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
) -> LandmarkListReturn:
    """[WIP] Get nearby landmarks grouped by area based on coordinates and optional filters."""
    return None
