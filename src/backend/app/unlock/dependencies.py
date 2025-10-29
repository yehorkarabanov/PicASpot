from typing import Annotated

from fastapi import Depends

from app.database import SessionDep

from .models import Unlock
from .repository import UnlockRepository
from .service import UnlockService


def get_unlock_repository(session: SessionDep) -> UnlockRepository:
    """Get an instance of UnlockRepository."""
    return UnlockRepository(session=session, model=Unlock)


UnlockRepDep = Annotated[UnlockRepository, Depends(get_unlock_repository)]


def get_unlock_service(unlock_repository: UnlockRepDep) -> UnlockService:
    """Get an instance of UnlockService."""
    return UnlockService(unlock_repository=unlock_repository)


UnlockServiceDep = Annotated[UnlockService, Depends(get_unlock_service)]
