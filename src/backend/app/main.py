from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.utils import generate_users
from app.database import dispose_engine
from app.database.manager import check_database_health
from app.database.redis import check_redis_health, close_redis, init_redis
from app.router import router
from app.settings import settings


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

app.include_router(router, prefix="/v1")


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
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks}
    )
