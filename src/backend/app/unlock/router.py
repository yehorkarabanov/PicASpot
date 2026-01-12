from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.auth.dependencies import CurrentUserDep
from app.core.schemas import BaseReturn

from .dependencies import UnlockServiceDep
from .schemas import (
    AttemptListRequestParams,
    AttemptListReturn,
    AttemptRequestParams,
    AttemptReturn,
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
async def get_unlock(
    unlock_id: UUID,
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


@router.get(
    "/attempts/{attempt_id}",
    response_model=AttemptReturn,
    response_model_exclude_none=True,
)
async def get_attempt(
    attempt_id: UUID,
    params: Annotated[AttemptRequestParams, Query()],
    unlock_service: UnlockServiceDep,
    current_user: CurrentUserDep,
) -> AttemptReturn:
    """
    Get attempt details by ID.

    This endpoint retrieves the details of a specific attempt for the current user.
    """
    attempt_details = await unlock_service.get_attempt_by_id(
        attempt_id=attempt_id, user=current_user, params=params
    )
    return AttemptReturn(
        data=attempt_details, message="Attempt details retrieved successfully."
    )


@router.get(
    "/attempts/", response_model=AttemptListReturn, response_model_exclude_none=True
)
async def list_attempts(
    params: Annotated[AttemptListRequestParams, Query()],
    unlock_service: UnlockServiceDep,
    current_user: CurrentUserDep,
) -> AttemptListReturn:
    """
    List all attempts for the current user.

    This endpoint retrieves a list of all attempts associated with the current user.
    """
    attempts = await unlock_service.list_attempts(user=current_user, params=params)
    return AttemptListReturn(
        data=attempts, message="Attempt list retrieved successfully."
    )
