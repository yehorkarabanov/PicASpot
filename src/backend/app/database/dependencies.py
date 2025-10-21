from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import get_async_session

# SessionDep is a type alias for injecting an AsyncSession into FastAPI route handlers.
# Usage: async def my_endpoint(session: SessionDep) -> dict:
# This provides a database session per request, with automatic commit/rollback and cleanup.
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
