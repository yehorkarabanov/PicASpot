import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import CurrentUserDep

from .dependencies import LandmarkServiceDep
from .schemas import (
    LandmarkCreate,
    LandmarkNearbyRequest,
    LandmarkReturn,
    LandmarkUpdate,
    NearbyLandmarksReturn,
)

router = APIRouter(prefix="/landmark", tags=["landmark"])


# IMPORTANT: Static routes (/nearby, /nearby-area) must be defined BEFORE
# dynamic routes (/{landmark_id}) to prevent "nearby" being interpreted as a UUID


@router.get(
    "/nearby", response_model=NearbyLandmarksReturn, response_model_exclude_none=True
)
async def get_nearby_landmarks(
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
    params: Annotated[LandmarkNearbyRequest, Query()],
) -> NearbyLandmarksReturn:
    """Get nearby landmarks based on coordinates and optional filters with pagination."""
    landmarks_data = await landmark_service.get_nearby_landmarks(
        data=params,
        user=current_user,
    )

    return NearbyLandmarksReturn(
        message="Nearby landmarks retrieved successfully", data=landmarks_data
    )


@router.post("/", response_model=LandmarkReturn, response_model_exclude_none=True)
async def create_landmark(
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
    landmark_data: Annotated[LandmarkCreate, Depends()],
) -> LandmarkReturn:
    """Create a new landmark."""
    landmark_response = await landmark_service.create_landmark(
        landmark_data=landmark_data, user=current_user
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
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
    landmark_data: Annotated[LandmarkUpdate, Depends()],
) -> LandmarkReturn:
    """Update landmark by ID."""
    landmark_response = await landmark_service.update_landmark(
        landmark_id=landmark_id, landmark_data=landmark_data, user=current_user
    )
    return LandmarkReturn(
        message="Landmark updated successfully", data=landmark_response
    )
