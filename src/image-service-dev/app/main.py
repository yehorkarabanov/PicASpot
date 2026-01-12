import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import setup_logging, shutdown_logging
from app.kafka import kafka_consumer, kafka_producer
from app.settings import settings
from app.storage import storage_service
from app.verification import verification_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup logging configuration
    setup_logging(use_file_logging=True)
    logger.info(
        f"{settings.SERVICE_NAME} starting up",
        extra={
            "service": settings.SERVICE_NAME,
            "debug_mode": settings.DEBUG,
        },
    )

    try:
        # Start MinIO storage service
        await storage_service.start()
        logger.info("Storage service started")

        # Start verification service (GeoMatchAI)
        await verification_service.start()
        logger.info("Verification service started")

        # Start Kafka producer for results
        await kafka_producer.start()
        logger.info("Kafka producer started")

        # Start Kafka consumer
        await kafka_consumer.start()
        await kafka_consumer.consume_messages()
        logger.info("Kafka consumer started")

    except Exception as e:
        logger.error(
            f"Failed to start {settings.SERVICE_NAME}",
            exc_info=True,
            extra={"error": str(e)},
        )
        raise

    yield

    logger.info(f"{settings.SERVICE_NAME} shutting down")
    try:
        await kafka_consumer.stop()
        await kafka_producer.stop()
        await verification_service.stop()
        await storage_service.stop()
    except Exception as e:
        logger.error(
            f"Error during {settings.SERVICE_NAME} shutdown",
            exc_info=True,
            extra={"error": str(e)},
        )
    finally:
        # Gracefully shutdown logging
        shutdown_logging()
        logger.info(f"{settings.SERVICE_NAME} stopped")


app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)


@app.get("/")
async def root():
    logger.debug("Root endpoint accessed")
    return {"message": f"{settings.SERVICE_NAME} is running."}


@app.get("/health")
async def health_check():
    logger.debug("Health check endpoint accessed")
    checks = {
        "storage": await storage_service.health_check(),
        "kafka_producer": await kafka_producer.health_check(),
    }
    all_healthy = all(checks.values())
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "checks": checks,
    }
