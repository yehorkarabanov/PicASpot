from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from .models import User
from app.database import SessionDep


async def get_user_repository(session: SessionDep):
    yield SQLAlchemyUserDatabase(session, User)


UserRepositoryDep = Annotated[
    SQLAlchemyUserDatabase[User], Depends(get_user_repository)
]