async def generate_users() -> None:
    from app.database.manager import async_session_maker
    from app.user.models import User
    from app.user.repository import UserRepository
    from app.user.service import UserService

    async with async_session_maker() as session:
        user_repo = UserRepository(session=session, model=User)
        user_service = UserService(user_repository=user_repo)
        await user_service.create_default_users()
