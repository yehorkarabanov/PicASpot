from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from .models import User
from app.database import SessionDep


async def get_user_repository(session: SessionDep):
    yield SQLAlchemyUserDatabase(session, User)