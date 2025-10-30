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
