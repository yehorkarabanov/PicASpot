from fastapi import APIRouter

from app.auth.router import router as auth_router
from app.users.router import router as users_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(users_router)
