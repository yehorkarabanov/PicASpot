from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import CurrentUserDep
from app.core.schemas import BaseReturn

from .dependencies import UnlockServiceDep
from .schemas import (
    UnlockCreate,
    UnlockListRequestParams,
    UnlockListReturn,
    UnlockRequestParams,
    UnlockReturn,
)

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


@router.get(
    "/{unlock_id}", response_model=UnlockReturn, response_model_exclude_none=True
)
async def get_unlocks(
    unlock_id: str,
    params: Annotated[UnlockRequestParams, Query()],
    unlock_service: UnlockServiceDep,
    current_user: CurrentUserDep,
) -> UnlockReturn:
    """
    Get unlock details by ID.

    This endpoint retrieves the details of a specific unlock for the current user.
    """
    unlock_details = await unlock_service.get_unlock_by_id(
        unlock_id=unlock_id, user=current_user, params=params
    )
    return UnlockReturn(
        data=unlock_details, message="Unlock details retrieved successfully."
    )


@router.get("/", response_model=UnlockListReturn, response_model_exclude_none=True)
async def list_unlocks(
    params: Annotated[UnlockListRequestParams, Query()],
    unlock_service: UnlockServiceDep,
    current_user: CurrentUserDep,
) -> UnlockListReturn:
    """
    List all unlocks for the current user.

    This endpoint retrieves a list of all unlocks associated with the current user.
    """
    unlocks = await unlock_service.list_unlocks(user=current_user, params=params)
    return UnlockListReturn(data=unlocks, message="Unlock list retrieved successfully.")
