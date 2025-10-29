from fastapi import APIRouter

from app.area.router import router as area_router
from app.auth.router import router as auth_router
from app.user.router import router as user_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(area_router)
