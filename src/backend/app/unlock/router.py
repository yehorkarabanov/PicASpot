from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.dependencies import CurrentUserDep
from app.core.schemas import BaseReturn

from .dependencies import UnlockServiceDep
from .schemas import UnlockCreate

router = APIRouter(prefix="/unlock", tags=["unlock"])


@router.post("/", response_model=BaseReturn)
async def create_unlock(
    unlock_service: UnlockServiceDep,
    current_user: CurrentUserDep,
    unlock_data: Annotated[UnlockCreate, Depends()],
) -> BaseReturn:
    """
    Create a new unlock (verify photo).

    This endpoint receives a photo and a landmark ID, uploads the photo,
    creates an unlock record, and sends a verification request to Kafka.
    """
    await unlock_service.create_unlock(unlock_data=unlock_data, user=current_user)
    return BaseReturn(message="Unlock request submitted successfully.")
