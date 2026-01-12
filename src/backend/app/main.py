import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.exception_handlers import (
    global_exception_handler,
    validation_exception_handler,
)
from app.core.logging import setup_logging, shutdown_logging
from app.core.utils import generate_users
from app.database import dispose_engine
from app.database.manager import check_database_health
from app.database.redis import check_redis_health, close_redis, init_redis
from app.kafka import ensure_topics_exist, kafka_consumer, kafka_producer
from app.middleware import (
    RateLimiterMiddleware,
    RequestLoggingMiddleware,
    TimeZoneMiddleware,
)
from app.router import router
from app.settings import settings
from app.storage import check_minio_health, ensure_bucket_exists

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup: Initialize Redis, Kafka, MinIO and create default users
    logger.info("Application startup initiated", extra={"debug_mode": settings.DEBUG})
    await init_redis()
    logger.info("Redis connection initialized")
    await ensure_topics_exist()
    logger.info("Kafka topics initialized")
    await kafka_producer.start()
    logger.info("Kafka producer initialized")
    await kafka_consumer.start()
    await kafka_consumer.consume_messages()
    logger.info("Kafka consumer initialized")
    await ensure_bucket_exists()
    logger.info("Default photos loaded into MinIO")
    await generate_users()
    logger.info("Default users created/verified")

    yield
    # Shutdown: Dispose engine, close Redis and Kafka
    logger.info("Application shutdown initiated")
    await kafka_consumer.stop()
    logger.info("Kafka consumer stopped")
    await kafka_producer.stop()
    logger.info("Kafka producer stopped")
    await dispose_engine()
    logger.info("Database engine disposed")
    await close_redis()
    logger.info("Redis connection closed")
    shutdown_logging()
    logger.info("Application shutdown completed")


app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    root_path="/api",
    lifespan=lifespan,
)

app.add_middleware(TimeZoneMiddleware)

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Timezone"],
)

app.add_middleware(
    RateLimiterMiddleware,
    max_requests=5,
    time_window=60,
    paths=[
        "/v1/auth/login",
        "/v1/auth/access-token",
        "/v1/auth/register",
        "/v1/auth/send-password-reset",
        "/v1/auth/verify",
    ],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)


static_path = Path(settings.STATIC_FILES_PATH)
if static_path.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(static_path)),
        name="static",
    )
    logger.info(f"Static files mounted at /static from {static_path}")
else:
    logger.warning(f"Static files directory not found at {static_path}")

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
        "minio": await check_minio_health(),
        "kafka": await kafka_producer.health_check(),
    }
    all_healthy = all(checks.values())
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
    )
