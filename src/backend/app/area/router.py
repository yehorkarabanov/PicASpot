import uuid

from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep

from .dependencies import AreaServiceDep
from .schemas import AreaCreate, AreaReturn

router = APIRouter(tags=["area"], prefix="/area")


@router.post("/", response_model=AreaReturn, response_model_exclude_none=True)
async def create_area(
    area_data: AreaCreate,
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
) -> AreaReturn:
    """Create a new area."""
    area_response = await area_service.create_area(
        area_data=area_data, created_by=current_user.id
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
