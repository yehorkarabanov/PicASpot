import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import CurrentUserDep

from .dependencies import LandmarkServiceDep
from .schemas import (
    LandmarkCreate,
    LandmarkListReturn,
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


@router.get(
    "/nearby-area", response_model=LandmarkListReturn, response_model_exclude_none=True
)
async def get_nearby_landmarks_grouped_by_area(
    landmark_service: LandmarkServiceDep,
    current_user: CurrentUserDep,
    latitude: Annotated[float, Query(ge=-90, le=90, description="Current latitude")],
    longitude: Annotated[
        float, Query(ge=-180, le=180, description="Current longitude")
    ],
    radius_meters: Annotated[
        int, Query(ge=1, le=50000, description="Search radius in meters")
    ] = 1000,
    area_id: Annotated[
        uuid.UUID | None, Query(description="Optional area ID to filter landmarks")
    ] = None,
    only_verified: Annotated[
        bool, Query(description="Only return landmarks from verified areas")
    ] = False,
    load_from_same_area: Annotated[
        bool, Query(description="Load all landmarks from same areas as found landmarks")
    ] = False,
) -> LandmarkListReturn:
    """[WIP] Get nearby landmarks grouped by area based on coordinates and optional filters."""
    # TODO: Implement nearby landmarks grouped by area logic in service
    return LandmarkListReturn(message="Not implemented yet", data=None)


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
