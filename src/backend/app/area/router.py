from fastapi import APIRouter

from app.auth.dependencies import CurrentUserDep

from .dependencies import AreaServiceDep
from .schemas import AreaReturn

router = APIRouter(tags=["area"], prefix="/area")


@router.post("/area", response_model=AreaReturn, response_model_exclude_none=True)
async def create_area(
    area_service: AreaServiceDep,
    current_user: CurrentUserDep,
) -> AreaReturn:
    """Create a new area."""
    pass
    # area_response = await area_service.create_area(created_by=current_user.id)
    # return AreaReturn(message="Area created successfully", data=area_response)
