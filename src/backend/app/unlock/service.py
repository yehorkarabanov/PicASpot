from .repository import UnlockRepository


class UnlockService:
    def __init__(self, unlock_repository: UnlockRepository):
        self.unlock_repository = unlock_repository
