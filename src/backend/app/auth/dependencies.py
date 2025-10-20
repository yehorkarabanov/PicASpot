from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionDep

from .models import User


async def get_user_repository(session: SessionDep):
    yield SQLAlchemyUserDatabase(session, User)


UserRepositoryDep = Annotated[
    SQLAlchemyUserDatabase[User, AsyncSession], Depends(get_user_repository)
]
