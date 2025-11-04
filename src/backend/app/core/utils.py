async def generate_users() -> None:
    import logging

    from app.area.models import Area  # noqa: F401
    from app.database.manager import async_session_maker
    from app.landmark.models import Landmark  # noqa: F401
    from app.unlock.models import Unlock  # noqa: F401
    from app.user.models import User  # noqa: F401
    from app.user.repository import UserRepository
    from app.user.service import UserService

    logger = logging.getLogger(__name__)

    async with async_session_maker() as session:
        user_repo = UserRepository(session=session, model=User)
        user_service = UserService(user_repository=user_repo)
        await user_service.create_default_users()
        logger.info("Default users generation completed")
