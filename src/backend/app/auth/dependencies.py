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


async def ActiveUserDep():
    # use like this
    # @app.get("/me")
    # async def read_current_user(user: ActiveUserDep):
    #     return user
    from .authentication import current_active_user

    return Annotated[User, Depends(current_active_user)]