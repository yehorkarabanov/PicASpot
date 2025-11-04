import datetime
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

logger = logging.getLogger(__name__)


def get_timezone_from_header(timezone_str: str) -> ZoneInfo:
    """
    Parse and validate timezone string from request header.

    Args:
        timezone_str: IANA timezone identifier (e.g., 'America/New_York', 'Europe/London')

    Returns:
        ZoneInfo: Validated timezone object, defaults to UTC if invalid
    """
    try:
        return ZoneInfo(timezone_str)
    except ZoneInfoNotFoundError:
        logger.warning(f"Invalid timezone '{timezone_str}' provided, defaulting to UTC")
        return ZoneInfo("UTC")


def get_utc_now() -> datetime.datetime:
    """
    Get current UTC datetime with timezone awareness.

    Returns:
        datetime.datetime: Current UTC datetime
    """
    return datetime.datetime.now(ZoneInfo("UTC"))


def convert_utc_to_timezone(
    utc_dt: datetime.datetime, timezone: ZoneInfo
) -> datetime.datetime:
    """
    Convert a UTC datetime to a specific timezone.

    Args:
        utc_dt: UTC datetime object
        timezone: Target timezone

    Returns:
        datetime.datetime: Datetime in the target timezone
    """
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
    return utc_dt.astimezone(timezone)


def convert_timezone_to_utc(
    dt: datetime.datetime, source_timezone: ZoneInfo | None = None
) -> datetime.datetime:
    """
    Convert a datetime from any timezone to UTC.

    Args:
        dt: Datetime object
        source_timezone: Source timezone if datetime is naive

    Returns:
        datetime.datetime: Datetime in UTC
    """
    if dt.tzinfo is None and source_timezone:
        dt = dt.replace(tzinfo=source_timezone)
    return dt.astimezone(ZoneInfo("UTC"))


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
