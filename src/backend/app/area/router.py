import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentSuperuserDep, CurrentUserDep

from .dependencies import AreaServiceDep
from .schemas import AreaCreate, AreaReturn, AreaUpdate

router = APIRouter(tags=["area"], prefix="/area")


@router.post("/", response_model=AreaReturn, response_model_exclude_none=True)
async def create_area(
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
    area_data: Annotated[AreaCreate, Depends()],
) -> AreaReturn:
    """Create a new area. If the user is a superuser, the area will be automatically verified."""
    area_response = await area_service.create_area(
        area_data=area_data, user=current_user
    )
    return AreaReturn(message="Area created successfully", data=area_response)


@router.get("/{area_id}", response_model=AreaReturn, response_model_exclude_none=True)
async def get_area(
    area_id: uuid.UUID,
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
) -> AreaReturn:
    """Get area by ID."""
    area_response = await area_service.get_area(area_id=area_id)
    return AreaReturn(message="Area retrieved successfully", data=area_response)


@router.delete(
    "/{area_id}",
    response_model=AreaReturn,
    response_model_exclude_none=True,
    description="Be careful, this will also delete all child areas!",
)
async def delete_area(
    area_id: uuid.UUID,
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
) -> AreaReturn:
    """Delete area by ID."""
    await area_service.delete_area(area_id=area_id, user=current_user)
    return AreaReturn(message="Area deleted successfully")


@router.patch("/{area_id}", response_model=AreaReturn, response_model_exclude_none=True)
async def update_area(
    area_id: uuid.UUID,
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
    area_data: Annotated[AreaUpdate, Depends()],
) -> AreaReturn:
    """Update area by ID."""
    area_response = await area_service.update_area(
        area_id=area_id, area_data=area_data, user=current_user
    )
    return AreaReturn(message="Area updated successfully", data=area_response)


@router.post(
    "/verify/{area_id}", response_model=AreaReturn, response_model_exclude_none=True
)
async def verify_area(
    area_id: uuid.UUID,
    area_service: AreaServiceDep,
    current_super_user: CurrentSuperuserDep,
) -> AreaReturn:
    """Verify area by ID."""
    area_response = await area_service.verify_area(
        area_id=area_id, super_user=current_super_user
    )
    return AreaReturn(message="Area verified successfully", data=area_response)
