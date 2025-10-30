import uuid

from .repository import AreaRepository
from .schemas import AreaCreate, AreaResponse


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository

    async def create_area(
        self, area_data: AreaCreate, created_by: uuid.UUID
    ) -> AreaResponse:
        """Create a new area with the given data and creator ID."""
        area_dict = area_data.model_dump()
        area_dict["created_by"] = created_by
        area = await self.area_repository.create(area_dict)
        return AreaResponse.model_validate(area)
