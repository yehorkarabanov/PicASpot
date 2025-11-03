import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.utils import generate_users
from app.database import dispose_engine
from app.database.manager import check_database_health
from app.database.redis import check_redis_health, close_redis, init_redis
from app.middleware.ratelimiter_middleware import RateLimiterMiddleware
from app.router import router
from app.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Initialize Redis and create default users
    await init_redis()
    await generate_users()

    yield
    # Shutdown: Dispose engine and close Redis
    await dispose_engine()
    await close_redis()


app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests=5,
    time_window=60,
    paths=["/v1/auth/login", "/v1/auth/register"],
)

app.include_router(router, prefix="/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={"path": request.url.path, "method": request.method},
    )
    if settings.DEBUG:
        raise exc
    return JSONResponse(status_code=500, content={"message": "Internal server error"})


@app.get("/")
async def root():
    return {"message": "Welcome to the picASpot API!"}


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    checks = {
        "redis": await check_redis_health(),
        "database": await check_database_health(),
    }
    all_healthy = all(checks.values())
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
    )
