# from fastapi import Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database.db_helper import
#
# async def get_user_db(session: AsyncSession = Depends(get_async_session)):
#     yield SQLAlchemyUserDatabase(session, User)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

SQLAlchemyUserDatabase()