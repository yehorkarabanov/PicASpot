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


def GetUserDep():
    # use like this
    # @app.get("/me")
    # async def read_current_user(user: GetUserDep()):
    #     return user  # noqa: ERA001
    from .authentication import current_active_user  # noqa: PLC0415

    return Annotated[User, Depends(current_active_user)]
