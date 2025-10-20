from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from .db_helper import db_helper

SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]
