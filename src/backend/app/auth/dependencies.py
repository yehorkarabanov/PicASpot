from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import UnauthorizedError
from app.user.dependencies import UserRepDep
from app.user.models import User

from .security import decode_token
from .service import AuthService


def get_auth_service(
    user_repository: UserRepDep,
) -> AuthService:
    return AuthService(user_repository=user_repository)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/access-token")


async def get_current_user(
    user_repository: UserRepDep,
    token: str = Depends(oauth2_scheme),
) -> User:
    """Get the current user from the JWT token."""
    payload = decode_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid token")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid token")

    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User not found")

    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_superuser(
    current_user: CurrentUserDep,
) -> User:
    """Get the current superuser."""
    if not current_user.is_superuser:
        raise UnauthorizedError("The user doesn't have enough privileges")
    return current_user

CurrentSuperuserDep = Annotated[User, Depends(get_current_superuser)]
