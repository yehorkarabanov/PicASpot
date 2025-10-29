from .repository import AreaRepository


class AreaService:
    def __init__(self, area_repository: AreaRepository):
        self.area_repository = area_repository
